// File: P4_Knapsack01.cs
using System;
using System.Collections.Generic;
using System.Linq;

class P3_Knapsack01
{
    static void Main()
    {
        var first = Console.ReadLine().Trim().Split();
        int N = int.Parse(first[0]);
        int C = int.Parse(first[1]);
        var w = new int[N];
        var v = new int[N];
		/*
		Formato A (una línea por objeto):
		5 10
		2 3
		3 4
		4 5
		7 10
		8 11


		Formato B (una sola línea compacta):
		5 10
		2 3 3 4 4 5 7 10 8 11
		*/
        for (int i = 0; i < N; i++)
        {
            var parts = Console.ReadLine().Trim().Split();
            w[i] = int.Parse(parts[0]);
            v[i] = int.Parse(parts[1]);
        }

        var (best, chosen) = Solve(w, v, C, N);
        Console.WriteLine(best);
        Console.WriteLine(string.Join(" ", chosen.Select(i => i + 1).OrderBy(x => x)));
    }

    static (int best, List<int> chosen) Solve(int[] w, int[] v, int C, int N)
    {
        var dp = new int[N + 1, C + 1];
        var take = new bool[N + 1, C + 1];

        for (int i = 1; i <= N; i++)
        {
            for (int c = 0; c <= C; c++)
            {
                dp[i, c] = dp[i - 1, c];
                if (c >= w[i - 1] && dp[i - 1, c - w[i - 1]] + v[i - 1] > dp[i, c])
                {
                    dp[i, c] = dp[i - 1, c - w[i - 1]] + v[i - 1];
                    take[i, c] = true;
                }
            }
        }

        var chosen = new List<int>();
        int ci = N, cc = C;
        while (ci > 0)
        {
            if (take[ci, cc])
            {
                chosen.Add(ci - 1);
                cc -= w[ci - 1];
            }
            ci--;
        }
        chosen.Sort();
        return (dp[N, C], chosen);
    }
}