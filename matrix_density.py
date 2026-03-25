import numpy as np

def analyze_matrix_distribution(A, output_file="matrix_metrics.txt"):
    """
    Compute spatial and statistical distribution measures for a binary (0/1) matrix
    and write the results to a text file.
    """

    # Convert to numpy array
    A = np.array(A)
    m, n = A.shape
    ones = np.argwhere(A == 1)
    N = len(ones)

    # If no 1s in matrix
    if N == 0:
        with open(output_file, "w") as f:
            f.write("Matrix has no 1s.\n")
        return

    # 1. Density
    density = N / (m * n)

    # 2. Row & column variances
    row_sums = A.sum(axis=1)
    col_sums = A.sum(axis=0)
    row_var = np.var(row_sums)
    col_var = np.var(col_sums)

    # 3. Spatial concentration (center of mass + spread)
    i_mean, j_mean = ones.mean(axis=0)
    spread = np.mean((ones[:,0] - i_mean)**2 + (ones[:,1] - j_mean)**2)

    # 4. Entropy of distribution
    p = np.zeros((m, n))
    p[A == 1] = 1 / N
    entropy = -np.sum(p[A == 1] * np.log(p[A == 1]))

    # Write results to file
    with open(output_file, "w") as f:
        f.write("=== Matrix Distribution Metrics ===\n\n")
        f.write(f"Matrix size: {m} x {n}\n")
        f.write(f"Number of 1s: {N}\n\n")
        f.write(f"Density: {density:.4f}\n")
        f.write(f"Row variance: {row_var:.4f}\n")
        f.write(f"Column variance: {col_var:.4f}\n")
        f.write(f"Center of mass: ({i_mean:.2f}, {j_mean:.2f})\n")
        f.write(f"Spatial spread: {spread:.4f}\n")
        f.write(f"Entropy: {entropy:.4f}\n")

    print(f"✅ Metrics written to '{output_file}'")

# Example usage
A = [
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 1]
]

analyze_matrix_distribution(A)
