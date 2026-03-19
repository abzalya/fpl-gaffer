1. random forest training (and all future models) ensure we are appropriately adressing categorical columns such as availability status and player position and team. currently they are numeric but it could be bad since one isnt any more important than the other. one hot encode position and teams going forward ?

2. currently model comparison will be done using only valuation metrics. is there a reason to allow predictions to be done by other models (that arent is_production) ?

3. bonus points are leakage. (EXCLUDED FROM FEATURES)

4. performance metrics to think about: Top-K Precision, NDCG, Weighted MAE, Spearman Rank Correlation. 

5. add print statements/logging to show progress as we go. 

6. predictor just predicted SARR to be top7 points gainer next week. Hes crystal palace and they dont have a fixture. update to make sure blank gameweeks are predicted 0. and somehow implement a double gameweek. 
f.e. if there is a missing fixture detail which would be there normally such as home etc. we can force points to 0
