from typing import List, Dict, Any, Tuple


def partition_grid(grid: List[List[Any]], strategy: str = 'vertical'):
    """
    将网格划分为不重叠的横向或纵向矩形
    strategy: 'horizontal' 优先横向, 'vertical' 优先纵向, 'auto' 自动选择数量少的
    """
    if not grid or not grid[0]:
        return []

    rows, cols = len(grid), len(grid[0])

    def solve(priority: str) -> List[Dict]:
        # covered矩阵跟踪已分配的格子
        covered = [[False] * cols for _ in range(rows)]
        rectangles = []

        def is_available(r: int, c: int) -> bool:
            return (0 <= r < rows and 0 <= c < cols and
                    not covered[r][c] and grid[r][c] is not None)

        if priority == 'horizontal':
            # 第一步：横向扫描，每行中连续的非None未覆盖格子组成横向矩形
            for r in range(rows):
                c = 0
                while c < cols:
                    if not is_available(r, c):
                        c += 1
                        continue

                    start_c = c
                    # 向右扩展到最长
                    while c < cols and is_available(r, c):
                        covered[r][c] = True
                        c += 1
                    end_c = c - 1

                    rectangles.append({
                        'type': 'horizontal',
                        'top_left': (r, start_c),
                        'bottom_right': (r, end_c),
                        'values': [grid[r][cc] for cc in range(start_c, end_c + 1)]
                    })

            # 第二步：纵向扫描处理剩余的零散格子
            for c in range(cols):
                r = 0
                while r < rows:
                    if not is_available(r, c):
                        r += 1
                        continue

                    start_r = r
                    while r < rows and is_available(r, c):
                        covered[r][c] = True
                        r += 1
                    end_r = r - 1

                    rectangles.append({
                        'type': 'vertical',
                        'top_left': (start_r, c),
                        'bottom_right': (end_r, c),
                        'values': [[grid[rr][c]] for rr in range(start_r, end_r + 1)]
                    })

        else:  # vertical priority
            # 第一步：纵向扫描
            for c in range(cols):
                r = 0
                while r < rows:
                    if not is_available(r, c):
                        r += 1
                        continue

                    start_r = r
                    while r < rows and is_available(r, c):
                        covered[r][c] = True
                        r += 1
                    end_r = r - 1

                    height = end_r - start_r + 1
                    rectangles.append({
                        'type': 'vertical',
                        'top_left': (start_r, c),
                        'bottom_right': (end_r, c),
                        'shape': (height, 1),
                        'values': [[grid[rr][c]] for rr in range(start_r, end_r + 1)]
                    })

            # 第二步：横向扫描处理剩余
            for r in range(rows):
                c = 0
                while c < cols:
                    if not is_available(r, c):
                        c += 1
                        continue

                    start_c = c
                    while c < cols and is_available(r, c):
                        covered[r][c] = True
                        c += 1
                    end_c = c - 1

                    width = end_c - start_c + 1
                    rectangles.append({
                        'type': 'horizontal',
                        'top_left': (r, start_c),
                        'bottom_right': (r, end_c),
                        'shape': (1, width),
                        'values': [grid[r][cc] for cc in range(start_c, end_c + 1)]
                    })

        return rectangles

    # 根据策略选择
    if strategy == 'auto':

        # 预计算：统计横纵向总长（指导策略）
        h_total = sum(1 for r in range(rows) for c in range(cols)
                      if grid[r][c] is not None and (c == 0 or grid[r][c - 1] is None))
        v_total = sum(1 for c in range(cols) for r in range(rows)
                      if grid[r][c] is not None and (r == 0 or grid[r - 1][c] is None))

        # 选择总长更长的方向优先（一次决策，非循环贪心）
        priority = 'horizontal' if h_total <= v_total else 'vertical'
        return solve(priority)
    else:
        return solve(strategy)

def partition_solid_optimized(grid: List[List[int]]) -> List[Dict]:
    """
    优化版实心矩形划分
    单次查找最大矩形: O(RC) 使用单调栈
    总体: O(K * RC)，K为矩形数量，实际运行很快
    """
    if not grid or not grid[0]:
        return []

    rows, cols = len(grid), len(grid[0])
    covered = [[False] * cols for _ in range(rows)]
    rectangles = []

    # 预处理：height[r][c] 表示从(r,c)向上（包括自己）连续未覆盖且有值的格子数
    def update_heights():
        height = [[0] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if not covered[r][c] and grid[r][c] is not None:
                    height[r][c] = 1 + (height[r - 1][c] if r > 0 else 0)
        return height

    # 单调栈找以第r行为底边的最大矩形
    def find_max_rectangle_in_row(height_row: List[int], r: int) -> Tuple[int, int, int]:
        """
        返回 (面积, 左列, 右列)
        标准直方图最大矩形算法 O(C)
        """
        stack = []  # 存储 (索引, 高度)
        max_area = 0
        best_l, best_r = 0, 0

        for c in range(cols + 1):
            # 末尾添加高度0的哨兵，确保栈清空
            h = height_row[c] if c < cols else 0

            while stack and (c == cols or h < stack[-1][1]):
                idx, hei = stack.pop()
                # 计算以hei为高的矩形
                left = stack[-1][0] + 1 if stack else 0
                right = c - 1
                area = hei * (right - left + 1)

                if area > max_area:
                    max_area = area
                    best_l, best_r = left, right

            stack.append((c, h))

        return max_area, best_l, best_r

    total_cells = sum(1 for row in grid for x in row if x is not None)
    covered_count = 0

    while covered_count < total_cells:
        height = update_heights()
        best_global = (0, 0, 0, 0, 0)  # (面积, r1, c1, r2, c2)

        # 对每一行找最大矩形，O(R*C)
        for r in range(rows):
            area, c1, c2 = find_max_rectangle_in_row(height[r], r)
            if area > best_global[0]:
                # 计算实际高度（由最小height决定）
                h = min(height[r][c] for c in range(c1, c2 + 1))
                r1 = r - h + 1
                best_global = (area, r1, c1, r, c2)

        if best_global[0] == 0:
            break

        _, r1, c1, r2, c2 = best_global

        # 标记覆盖
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if not covered[r][c]:
                    covered[r][c] = True
                    covered_count += 1

        # 提取值
        values = [grid[r][c1:c2 + 1] for r in range(r1, r2 + 1)]

        rectangles.append({
            'type': 'solid',
            'top_left': (r1, c1),
            'bottom_right': (r2, c2),
            'shape': (r2 - r1 + 1, c2 - c1 + 1),
            'values': values
        })

    return rectangles


def print_partitions(grid: List[List[int]], rectangles: List[Dict]):
    """打印划分结果"""
    print(f"共划分为 {len(rectangles)} 个无重叠矩形：\n")

    # 验证覆盖
    rows, cols = len(grid), len(grid[0])
    verification = [[None] * cols for _ in range(rows)]

    for idx, rect in enumerate(rectangles, 1):
        tl, br = rect['top_left'], rect['bottom_right']
        rect_type = rect['type']
        values = rect['values']

        # 标记验证矩阵
        if rect_type == 'horizontal':
            for c in range(tl[1], br[1] + 1):
                verification[tl[0]][c] = idx
            display = f"[{', '.join(map(str, values))}]"
        else:
            for r in range(tl[0], br[0] + 1):
                verification[r][tl[1]] = idx
            display = str(values).replace(' ', '')

        print(f"区域 {idx}:")
        print(f"  类型: {'横向' if rect_type == 'horizontal' else '纵向'}")
        print(f"  左上角: {tl}")
        print(f"  右下角: {br}")
        print(f"  值: {display}")
        print()

    # 打印验证图
    print("划分验证图（数字代表区域编号，. 代表 None）：")
    for r in range(rows):
        row_str = ""
        for c in range(cols):
            if grid[r][c] is None:
                row_str += ". "
            else:
                row_str += f"{verification[r][c] if verification[r][c] is not None else '?'} "
        print(f"  {row_str}")


# ==================== 测试 ====================

if __name__ == "__main__":
    test_grid = [
        [1, 1, None, "asdasd", 2],
        [1, 1, 1, 2.231, 2],
        [None, 1, 1, None, 2],
        [None, {"a":2}, None, 3, 3],
        [4, 4, None, 3, None]
    ]

    print("原始网格（. 表示 None）：")
    for row in test_grid:
        print([str(x) if x is not None else "." for x in row])
    print()

    # 分别测试两种策略
    print("=" * 50)
    print("【策略：横向优先】")
    print("=" * 50)
    h_result = partition_grid(test_grid, 'horizontal')
    print_partitions(test_grid, h_result)

    print("\n" + "=" * 50)
    print("【策略：纵向优先】")
    print("=" * 50)
    v_result = partition_grid(test_grid, 'vertical')
    print_partitions(test_grid, v_result)

    print("\n" + "=" * 50)
    print("【策略：自动选择（数量少）】")
    print("=" * 50)
    best_result = partition_grid(test_grid, 'auto')
    print(f"自动选择了 {'横向' if len(h_result) <= len(v_result) else '纵向'} 优先策略")
    print_partitions(test_grid, best_result)

    # 测试实心矩形（优化版）
    solid_rects = partition_solid_optimized(test_grid)

    for i, r in enumerate(solid_rects, 1):
        print(f"  {i}: {r['top_left']}->{r['bottom_right']} {r['shape']}, values: {r['values']}")