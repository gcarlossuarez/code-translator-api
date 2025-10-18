// File: P2_SubsetSum.cs
using System;
using System.Collections.Generic;
using System.Linq;

class P1_SubsetSum
{
    static void Main()
    {
        var first = Console.ReadLine().Trim().Split();
        int N = int.Parse(first[0]);
        int C = int.Parse(first[1]);
        var w = Console.ReadLine().Trim().Split().Select(int.Parse).ToArray();

        var (ok, chosen) = Solve(w, C, N);
        if (!ok) { Console.WriteLine("NO"); return; }
        Console.WriteLine("YES");
        Console.WriteLine(string.Join(" ", chosen.Select(i => i + 1).OrderBy(x => x)));
    }

    static (bool ok, List<int> chosen) Solve(int[] a, int T, int N)
    {
        var dp = new bool[N + 1, T + 1];
        var parent = new (int i, int s, int? take)[N + 1, T + 1];
        dp[0, 0] = true;

        for (int i = 1; i <= N; i++)
        {
            for (int s = 0; s <= T; s++)
            {
                if (dp[i - 1, s])
                {
                    dp[i, s] = true;
                    parent[i, s] = (i - 1, s, 0);
                }
                if (s >= a[i - 1] && dp[i - 1, s - a[i - 1]])
                {
                    dp[i, s] = true;
                    parent[i, s] = (i - 1, s - a[i - 1], 1);
                }
            }
        }

        if (!dp[N, T]) return (false, new List<int>());
        var res = new List<int>();
        int ci = N, cs = T;
        while (ci > 0)
        {
            var p = parent[ci, cs];
            if (p.take == 1) res.Add(ci - 1);
            ci = p.i; cs = p.s;
        }
        res.Sort();
        return (true, res);
    }
}
