"""
王牌钓手 前置依赖图谱引擎
======================
功能：
- 构建知识点之间的前置依赖有向图
- 根据错题追溯到根因薄弱点
- 生成"回炉路径"（从根因→错题知识点的学习顺序）
- 计算知识点的"解锁条件"
"""

import json
from pathlib import Path
from collections import defaultdict, deque
from typing import Optional

BANK_DIR = Path(__file__).resolve().parent.parent / "data"


class PrerequisiteGraph:
    """知识点前置依赖有向图"""

    def __init__(self, atlas_path: Path = None):
        if atlas_path is None:
            atlas_path = BANK_DIR / "knowledge_atlas.json"
        with open(atlas_path, "r", encoding="utf-8") as f:
            self.atlas = json.load(f)

        self.kp_map = {}  # id → knowledge_point
        self.prereqs = defaultdict(list)  # kp_id → [前置kp_id列表]
        self.dependents = defaultdict(list)  # kp_id → [依赖它的kp_id列表]

        for kp in self.atlas.get("knowledge_points", []):
            kp_id = kp["id"]
            self.kp_map[kp_id] = kp
            pre = kp.get("prerequisites", [])
            self.prereqs[kp_id] = pre
            for p in pre:
                self.dependents[p].append(kp_id)

    def get_kp(self, kp_id: str) -> Optional[dict]:
        return self.kp_map.get(kp_id)

    def get_prerequisites(self, kp_id: str) -> list:
        """直接前置知识点"""
        return self.prereqs.get(kp_id, [])

    def get_all_prerequisites(self, kp_id: str) -> list:
        """所有前置知识点（递归，包含间接依赖）"""
        visited = set()
        result = []
        queue = deque(self.prereqs.get(kp_id, []))
        while queue:
            pre_id = queue.popleft()
            if pre_id in visited:
                continue
            visited.add(pre_id)
            result.append(pre_id)
            for pp in self.prereqs.get(pre_id, []):
                if pp not in visited:
                    queue.append(pp)
        return result

    def get_dependents(self, kp_id: str) -> list:
        """直接依赖它的知识点"""
        return self.dependents.get(kp_id, [])

    def get_all_dependents(self, kp_id: str) -> list:
        """所有依赖它的知识点（递归）"""
        visited = set()
        result = []
        queue = deque(self.dependents.get(kp_id, []))
        while queue:
            dep_id = queue.popleft()
            if dep_id in visited:
                continue
            visited.add(dep_id)
            result.append(dep_id)
            for dd in self.dependents.get(dep_id, []):
                if dd not in visited:
                    queue.append(dd)
        return result

    def find_root_causes(self, wrong_kp_ids: list) -> dict:
        """
        核心：找到错题知识点的根因薄弱点。
        
        逻辑：对于每个做错的知识点，
        - 检查它的所有前置知识点
        - 如果前置知识点本身也是 locked 或者也是错的，递归追溯
        - 返回"根因链"：从根因到错题点的路径

        返回 {错题kp_id: {"root_cause": 根因kp_id, "chain": [根因, 中间, 错题]}}
        """
        results = {}
        for kp_id in wrong_kp_ids:
            all_pre = self.get_all_prerequisites(kp_id)
            # 根因 = 最底层的前置（没有前置的，或者是已解锁但没掌握的）
            root = kp_id
            chain = [kp_id]
            if all_pre:
                # 找到最底层的前置
                for pre_id in reversed(all_pre):  # 从最早的前置开始
                    pre_kp = self.kp_map.get(pre_id)
                    if pre_kp and pre_kp.get("status") != "mastered":
                        root = pre_id
                        break
                # 构建从根因到错题的链
                chain = self._find_path(root, kp_id)
            results[kp_id] = {
                "root_cause": root,
                "chain": chain,
                "chain_names": [self.get_name(c) for c in chain],
            }
        return results

    def _find_path(self, from_id: str, to_id: str) -> list:
        """BFS 找从 from 到 to 的最短路径"""
        if from_id == to_id:
            return [from_id]

        visited = {from_id}
        queue = deque([(from_id, [from_id])])
        while queue:
            current, path = queue.popleft()
            for dep in self.dependents.get(current, []):
                if dep in visited:
                    continue
                new_path = path + [dep]
                if dep == to_id:
                    return new_path
                visited.add(dep)
                queue.append((dep, new_path))
        return [from_id, to_id]  # fallback

    def generate_rewarm_path(self, wrong_kp_ids: list) -> list:
        """
        生成回炉路径：按拓扑顺序排列需要复习的知识点。
        从根因开始，逐层修复，最后回到错题点。
        """
        all_points = set()
        for kp_id in wrong_kp_ids:
            all_points.add(kp_id)
            for pre in self.get_all_prerequisites(kp_id):
                all_points.add(pre)

        # 拓扑排序
        return self._topo_sort(list(all_points))

    def _topo_sort(self, kp_ids: list) -> list:
        """对知识点ID列表进行拓扑排序（前置先于后继）"""
        in_degree = {kp: 0 for kp in kp_ids}
        adj = {kp: [] for kp in kp_ids}

        for kp in kp_ids:
            for pre in self.prereqs.get(kp, []):
                if pre in kp_ids:
                    adj[pre].append(kp)
                    in_degree[kp] = in_degree.get(kp, 0) + 1

        queue = deque([kp for kp in kp_ids if in_degree.get(kp, 0) == 0])
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result

    def get_unlocked(self) -> list:
        """获取所有已解锁的知识点"""
        return [kp for kp in self.kp_map.values()
                if kp.get("status") in ("unlocked", "mastered")]

    def get_locked(self) -> list:
        """获取所有未解锁的知识点"""
        return [kp for kp in self.kp_map.values()
                if kp.get("status") == "locked"]

    def get_unlockable(self) -> list:
        """获取可以解锁的知识点（前置条件已满足）"""
        unlockable = []
        for kp_id, kp in self.kp_map.items():
            if kp.get("status") == "locked":
                pre_met = all(
                    self.kp_map.get(p, {}).get("status") == "mastered"
                    for p in self.prereqs.get(kp_id, [])
                )
                if pre_met:
                    unlockable.append(kp)
        return unlockable

    def get_name(self, kp_id: str) -> str:
        kp = self.kp_map.get(kp_id)
        return kp["name"] if kp else kp_id

    def get_category(self, kp_id: str) -> str:
        kp = self.kp_map.get(kp_id)
        return kp.get("category", "") if kp else ""

    def print_path(self, path: list) -> str:
        """美化的路径打印"""
        names = []
        for kp_id in path:
            kp = self.kp_map.get(kp_id, {})
            emoji = "🔒" if kp.get("status") == "locked" else "🗝️"
            names.append(f"{emoji} {kp.get('name', kp_id)}")
        return " → ".join(names)

    def summary(self) -> dict:
        """图谱概览"""
        total = len(self.kp_map)
        unlocked = len(self.get_unlocked())
        mastered = len([kp for kp in self.kp_map.values()
                        if kp.get("status") == "mastered"])
        locked = total - unlocked - mastered
        unlockable = len(self.get_unlockable())

        # 找最长的前置链
        max_chain = 0
        max_chain_kp = ""
        for kp_id in self.kp_map:
            chain = self.get_all_prerequisites(kp_id)
            if len(chain) > max_chain:
                max_chain = len(chain)
                max_chain_kp = kp_id

        return {
            "total": total,
            "unlocked": unlocked,
            "mastered": mastered,
            "locked": locked,
            "unlockable": unlockable,
            "longest_prereq_chain": max_chain,
            "longest_chain_kp": self.get_name(max_chain_kp),
        }


# ---------- CLI ----------

def cli():
    import sys
    pg = PrerequisiteGraph()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python prerequisite_graph.py summary       — 图谱概览")
        print("  python prerequisite_graph.py pre <kp_id>   — 查看前置依赖")
        print("  python prerequisite_graph.py dep <kp_id>   — 查看被依赖项")
        print("  python prerequisite_graph.py root <kp_id>  — 追溯根因")
        print("  python prerequisite_graph.py path <kps>    — 回炉路径（逗号分隔）")
        return

    cmd = sys.argv[1]

    if cmd == "summary":
        s = pg.summary()
        print(f"知识点总数: {s['total']}")
        print(f"  已解锁: {s['unlocked']}  已掌握: {s['mastered']}  锁定: {s['locked']}")
        print(f"  可解锁: {s['unlockable']}")
        print(f"最长前置链: {s['longest_prereq_chain']}层 ({s['longest_chain_kp']})")

    elif cmd == "pre":
        kp_id = sys.argv[2]
        kp = pg.get_kp(kp_id)
        if not kp:
            print(f"知识点 {kp_id} 不存在")
            return
        print(f"知识点: {kp['name']} ({kp['subject']}/{kp['category']})")
        print(f"状态: {kp['status']}")
        print(f"直接前置:")
        for pre in pg.get_prerequisites(kp_id):
            print(f"  → {pg.get_name(pre)} [{pre}]")
        all_pre = pg.get_all_prerequisites(kp_id)
        if all_pre:
            print(f"所有前置 ({len(all_pre)}个):")
            for pre in sorted(all_pre):
                print(f"  → {pg.get_name(pre)} [{pre}]")

    elif cmd == "dep":
        kp_id = sys.argv[2]
        deps = pg.get_all_dependents(kp_id)
        if deps:
            print(f"依赖 {pg.get_name(kp_id)} 的知识点 ({len(deps)}个):")
            for dep in sorted(deps):
                print(f"  → {pg.get_name(dep)} [{dep}]")
        else:
            print(f"没有知识点依赖 {pg.get_name(kp_id)}")

    elif cmd == "root":
        kp_id = sys.argv[2]
        results = pg.find_root_causes([kp_id])
        for kp, info in results.items():
            print(f"错题点: {pg.get_name(kp)}")
            print(f"根因: {pg.get_name(info['root_cause'])}")
            print(f"修复路径: {pg.print_path(info['chain'])}")

    elif cmd == "path":
        kp_ids = sys.argv[2].split(",")
        path = pg.generate_rewarm_path(kp_ids)
        print("回炉路径（从根因到高级）:")
        for i, kp_id in enumerate(path):
            print(f"  {i+1}. {pg.get_name(kp_id)} [{kp_id}] ({pg.get_category(kp_id)})")


if __name__ == "__main__":
    cli()
