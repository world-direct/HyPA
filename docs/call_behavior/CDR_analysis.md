# CDR analysis

The following data has been evaluated for the year `2023` starting from `2023-01-01 00:00:00.000` till `2023-12-01 00:00:000.000`:
- 11 months evaluated
- datasource: HCS CDRs database
- a total of `1241` clients evaluated


## Call range per customer

First we count clients having calls within a fixed call range:

| number of clients | call range | client coverage |
|-------------------|------------|-----------------|
| 397 | x < 10000 | 31.99 % |
| 658 | 10000 <= x < 100000  | 53.02 % |
| 178 | 100000 <= x < 1000000 | 14.34 % |
| 8 | 1000000 <= x | 0.65 % |

- We see most of the clients `53.02 %` are within a call range of `100000 calls to 1000000 calls`
- `85.01 %` of all clients are till a maximum of `100000` calls


## Total calls

For the given time range we got a total of `89964036` calls:

| call range | calls | call coverage |
|------------|-------|---------------|
| x < 10000 | 1487947 | 1.65 % |
| 10000 <= x < 100000 | 24371924 | 27.09 % |
| 100000 <= x < 1000000 | 44294452 | 49.24 % |
| 1000000 <= x | 19809713 | 22.02 % |


## Calculate weighting

We can see that there are many clients that have little calls, but also a few clients that produce many calls:

| call range | client coverage | call coverage |
|------------|-----------------|---------------|
| x < 10000 | 31.99 % | 1.65 % |
| 10000 <= x < 100000 | 53.02 % | 27.09 % |
| 100000 <= x < 1000000 | 14.34 % | 49.24 % |
| 1000000 <= x | 0.65 % | 22.02 % |


## Average calls per hour-of-day

### x < 10000

| Hour_of_Day |	Total_Calls_all_Clients | Average_Calls_all_Clients | Total_Calls_single_Client | Mean_Calls_single_Client | Std_Calls_single_Client |
|-------------|-------------------------|---------------------------|---------------------------|--------------------------|-------------------------|
| 0	 | 1997   | 26  | 6   | 1 | 1 |
| 1	 | 1386   | 25  | 4   | 1 | 1 |
| 2	 | 1030   | 21  | 3   | 1 | 1 |
| 3	 | 995    | 22  | 3   | 1 | 1 |
| 4	 | 1301   | 23  | 4   | 1 | 1 |
| 5	 | 1426   | 15  | 4   | 1 | 1 |
| 6	 | 7355   | 31  | 19  | 1 | 1 |
| 7	 | 52399  | 156 | 132 | 1 | 1 |
| 8	 | 171431 | 469 | 432 | 2 | 2 |
| 9	 | 215693 | 589 | 544 | 2 | 2 |
| 10 | 220635 | 601 | 556 | 2 | 2 |
| 11 | 213747 | 568 | 539 | 2 | 2 |
| 12 | 98940  | 266 | 250 | 1 | 1 |
| 13 | 133788 | 359 | 337 | 1 | 1 |
| 14 | 131367 | 350 | 331 | 1 | 1 |
| 15 | 109279 | 294 | 276 | 1 | 1 |
| 16 | 70078  | 191 | 177 | 1 | 1 |
| 17 | 25172  | 73  | 64  | 1 | 1 |
| 18 | 11016  | 35  | 28  | 1 | 1 |
| 19 | 6901   | 25  | 18  | 1 | 1 |
| 20 | 4742   | 20  | 12  | 1 | 1 |
| 21 | 3015   | 16  | 8   | 1 | 1 |
| 22 | 2103   | 15  | 6   | 1 | 1 |
| 23 | 2151   | 21  | 6   | 1 | 1 |


### 10000 <= x < 100000

| Hour_of_Day |	Total_Calls_all_Clients | Average_Calls_all_Clients | Total_Calls_single_Client | Mean_Calls_single_Client | Std_Calls_single_Client |
|-------------|-------------------------|---------------------------|---------------------------|--------------------------|-------------------------|
| 0	 | 16799   | 44   | 26   | 1 | 1 |
| 1	 | 13722   | 44   | 21   | 1 | 1 |
| 2	 | 10250   | 38   | 16   | 1 | 1 |
| 3	 | 14293   | 56   | 22   | 1 | 1 |
| 4	 | 12367   | 42   | 19   | 1 | 1 |
| 5	 | 20652   | 42   | 32   | 1 | 1 |
| 6	 | 107145  | 166  | 163  | 1 | 1 |
| 7	 | 939196  | 1427 | 1428 | 3 | 3 |
| 8	 | 2984109 | 4535 | 4536 | 7 | 5 |
| 9	 | 3619062 | 5500 | 5501 | 9 | 6 |
| 10 | 3545463 | 5388 | 5389 | 9 | 6 |
| 11 | 3268292 | 4967 | 4968 | 8 | 5 |
| 12 | 1449812 | 2203 | 2204 | 4 | 3 |
| 13 | 2180329 | 3313 | 3314 | 6 | 4 |
| 14 | 2172810 | 3302 | 3303 | 6 | 4 |
| 15 | 1855140 | 2819 | 2820 | 5 | 4 |
| 16 | 1199292 | 1822 | 1823 | 3 | 3 |
| 17 | 466169  | 708  | 709  | 2 | 2 |
| 18 | 208322  | 318  | 317  | 1 | 2 |
| 19 | 108885  | 167  | 166  | 1 | 1 |
| 20 | 74692   | 117  | 114  | 1 | 1 |
| 21 | 52268   | 86   | 80   | 1 | 1 |
| 22 | 31956   | 59   | 49   | 1 | 1 |
| 23 | 20899   | 46   | 32   | 1 | 1 |


### 100000 <= x < 1000000

| Hour_of_Day |	Total_Calls_all_Clients | Average_Calls_all_Clients | Total_Calls_single_Client | Mean_Calls_single_Client | Std_Calls_single_Client |
|-------------|-------------------------|---------------------------|---------------------------|--------------------------|-------------------------|
| 0	 | 91434   | 544   | 514   | 4   | 12  |
| 1	 | 96229   | 597   | 541   | 4   | 15  |
| 2	 | 90795   | 626   | 511   | 4   | 14  |
| 3	 | 83843   | 578   | 472   | 4   | 12  |
| 4	 | 82834   | 537   | 466   | 4   | 11  |
| 5	 | 105599  | 617   | 594   | 4   | 12  |
| 6	 | 255280  | 1434  | 1435  | 9   | 15  |
| 7	 | 1614247 | 9068  | 9069  | 51  | 51  |
| 8	 | 5037308 | 28299 | 28300 | 159 | 142 |
| 9	 | 6110316 | 34327 | 34328 | 193 | 147 |
| 10 | 6030615 | 33879 | 33880 | 191 | 142 |
| 11 | 5516786 | 30993 | 30994 | 175 | 131 |
| 12 | 2865929 | 16100 | 16101 | 91  | 87  |
| 13 | 4047567 | 22739 | 22740 | 128 | 99  |
| 14 | 4011720 | 22537 | 22538 | 127 | 96  |
| 15 | 3448755 | 19375 | 19376 | 109 | 86  |
| 16 | 2364030 | 13281 | 13282 | 75  | 70  |
| 17 | 1138176 | 6394  | 6395  | 36  | 47  |
| 18 | 458001  | 2573  | 2574  | 15  | 27  |
| 19 | 279011  | 1567  | 1568  | 9   | 21  |
| 20 | 199395  | 1120  | 1121  | 7   | 16  |
| 21 | 145413  | 826   | 817   | 5   | 13  |
| 22 | 119901  | 681   | 674   | 4   | 13  |
| 23 | 101268  | 582   | 569   | 4   | 12  |


### 1000000 <= x

| Hour_of_Day |	Total_Calls_all_Clients | Average_Calls_all_Clients | Total_Calls_single_Client | Mean_Calls_single_Client | Std_Calls_single_Client |
|-------------|-------------------------|---------------------------|---------------------------|--------------------------|-------------------------|
| 0	 | 1067   | 133   | 133   | 16   | 43   |
| 1	 | 771    | 96    | 96    | 12   | 30   |
| 2	 | 571    | 71    | 71    | 9    | 22   |
| 3	 | 403    | 50    | 50    | 6    | 14   |
| 4	 | 458    | 57    | 57    | 7    | 15   |
| 5	 | 1010   | 126   | 126   | 15   | 30   |
| 6	 | 9264   | 1158  | 1158  | 144  | 197  |
| 7	 | 62987  | 7873  | 7873  | 984  | 1128 |
| 8	 | 196441 | 24555 | 24555 | 3069 | 3478 |
| 9	 | 267987 | 33498 | 33498 | 4187 | 3900 |
| 10 | 268546 | 33568 | 33568 | 4196 | 3954 |
| 11 | 249663 | 31207 | 31208 | 3901 | 3705 |
| 12 | 157984 | 19748 | 19748 | 2468 | 2012 |
| 13 | 195717 | 24464 | 24464 | 3058 | 3318 |
| 14 | 193651 | 24206 | 24206 | 3025 | 3333 |
| 15 | 185711 | 23213 | 23214 | 2901 | 3009 |
| 16 | 115402 | 14425 | 14425 | 1803 | 1790 |
| 17 | 46479  | 5809  | 5809  | 726  | 642  |
| 18 | 11368  | 1421  | 1421  | 177  | 326  |
| 19 | 5977   | 747   | 747   | 93   | 211  |
| 20 | 3773   | 471   | 471   | 59   | 139  |
| 21 | 2343   | 292   | 292   | 36   | 86   |
| 22 | 1758   | 219   | 219   | 27   | 68   |
| 23 | 1630   | 203   | 203   | 25   | 66   |

### Evaluation

We can see that that call range `1000000 <= x` is an outlier, as it produces `22.02 %` of all calls with just `0.65 %` of all clients.
Thus we propose the following weighting by `client coverage`:

```py
avg_calls_hour_of_day = (x < 10000) calls * 31.99 %
                        + (10000 <= x < 100000) calls * 53.02 %
                        + (100000 <= x < 1000000) calls * 14.34 %
                        + (1000000 <= x) calls * 0.65 %
```

| Hour_of_Day | x < 10000 | 10000 <= x < 100000 | 100000 <= x < 1000000 | 1000000 <= x | weighted |
|-------------|-----------|---------------------|-----------------------|--------------|----------|
| 0  | 1 | 1 | 4   | 167   | 3   |
| 1  | 1 | 1 | 4   | 121   | 3   |
| 2  | 1 | 1 | 4   | 90    | 3   |
| 3  | 1 | 1 | 4   | 63    | 2   |
| 4  | 1 | 1 | 4   | 72    | 2   |
| 5  | 1 | 1 | 4   | 158   | 3   |
| 6  | 1 | 1 | 9   | 1448  | 12  |
| 7  | 1 | 3 | 51  | 9842  | 74  |
| 8  | 2 | 7 | 159 | 30694 | 227 |
| 9  | 2 | 9 | 193 | 41873 | 306 |
| 10 | 2 | 9 | 191 | 41961 | 306 |
| 11 | 2 | 8 | 175 | 39010 | 284 |
| 12 | 1 | 4 | 91  | 24685 | 176 |
| 13 | 1 | 6 | 128 | 30581 | 221 |
| 14 | 1 | 6 | 127 | 30258 | 219 |
| 15 | 1 | 5 | 109 | 29018 | 208 |
| 16 | 1 | 3 | 75  | 18032 | 130 |
| 17 | 1 | 2 | 36  | 7263  | 54  |
| 18 | 1 | 1 | 15  | 1777  | 15  |
| 19 | 1 | 1 | 9   | 934   | 9   |
| 20 | 1 | 1 | 7   | 590   | 6   |
| 21 | 1 | 1 | 5   | 366   | 4   |
| 22 | 1 | 1 | 4   | 275   | 4   |
| 23 | 1 | 1 | 4   | 255   | 4   |

These `weighted call values` will be used for call testing!