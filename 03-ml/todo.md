1. random forest training (and all future models) ensure we are appropriately adressing categorical columns such as availability status and player position and team. currently they are numeric but it could be bad since one isnt any more important than the other. one hot encode position and teams going forward ?

2. currently model comparison will be done using only valuation metrics. is there a reason to allow predictions to be done by other models (that arent is_production) ?

3. bonus points are leakage. (EXCLUDED FROM FEATURES)

4. performance metrics to think about: Top-K Precision, NDCG, Weighted MAE, Spearman Rank Correlation. 

5. add print statements to show progress as we go. 