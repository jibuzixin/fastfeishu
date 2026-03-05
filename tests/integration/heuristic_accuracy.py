from fastfeishu.utils.partition_grid import partition_grid
import random
import time  # 新增导入


# 随机生成测试数据
def generate_random_grid(rows=10, cols=10, density=0.7):
    """生成随机网格，density为填充率"""
    return [[random.randint(1, 9) if random.random() < density else None for _ in range(cols)] for _ in range(rows)]


# 测试启发式准确率
def test_heuristic_accuracy(trials=1000):
    correct = 0
    total_diff = 0  # 选错时的差距累计
    total_auto_time = 0  # 启发式选择总耗时
    total_exact_time = 0  # 精确计算总耗时

    for _ in range(trials):
        grid = generate_random_grid(rows=1000, cols=35, density=0.7)

        # 启发式选择 - 计时
        t1 = time.perf_counter()
        h_result = partition_grid(grid, 'auto')
        h_count = len(h_result)
        t2 = time.perf_counter()
        total_auto_time += (t2 - t1)

        # 精确比较 - 计时（分别计算两种策略取最优）
        t3 = time.perf_counter()
        exact_h = partition_grid(grid, 'horizontal')
        exact_v = partition_grid(grid, 'vertical')
        optimal = min(len(exact_h), len(exact_v))
        t4 = time.perf_counter()
        total_exact_time += (t4 - t3)

        if h_count == optimal:
            correct += 1
        else:
            total_diff += (h_count - optimal)

    accuracy = correct / trials
    avg_diff = total_diff / (trials - correct) if (trials - correct) > 0 else 0
    avg_auto_time = total_auto_time / trials
    avg_exact_time = total_exact_time / trials

    return accuracy, avg_diff, avg_auto_time, avg_exact_time


if __name__ == "__main__":
    print("测试启发式准确率（1000次随机网格）...")
    acc, diff, auto_time, exact_time = test_heuristic_accuracy(1000)

    # 转换为毫秒便于阅读
    auto_ms = auto_time * 1000
    exact_ms = exact_time * 1000
    speedup = exact_time / auto_time if auto_time > 0 else float('inf')

    print(f"准确率: {acc:.1%}")
    print(f"选错时平均多产生的矩形数: {diff:.2f}")
    print(f"\n性能统计:")
    print(f"  启发式('auto')平均耗时: {auto_ms:.3f} ms")
    print(f"  精确计算平均耗时: {exact_ms:.3f} ms")
    print(f"  加速比: {speedup:.1f}x")
    print(
        f"\n结论: 启发式在 {acc:.1%} 的情况下选择了最优或并列最优策略，平均耗时 {auto_ms:.2f}ms，比精确计算快 {speedup:.1f} 倍")
