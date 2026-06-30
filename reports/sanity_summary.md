# Fresh Unseen Sanity Test Summary

- **Count of images tested:** 10
- **Number predicted real:** 7
- **Number predicted screen:** 3
- **Number in borderline zone (0.35-0.65):** 2
- **Average real score:** 0.1450
- **Average screen score:** 0.7195
- **False positives (real predicted as screen):** 0
- **False negatives (screen predicted as real):** 2

## Individual Results
| filepath                               | true_label   |   final_score |   predicted_label | correct   |
|:---------------------------------------|:-------------|--------------:|------------------:|:----------|
| manual_test\unknown\bonfire.jpg        | screen       |     0.956798  |                 1 | True      |
| manual_test\unknown\dice.png           | screen       |     0.95742   |                 1 | True      |
| manual_test\unknown\flower.jpeg        | screen       |     0.41435   |                 0 | False     |
| manual_test\unknown\flower_screen.jpeg | screen       |     0.975469  |                 1 | True      |
| manual_test\unknown\real\books.png     | real         |     0.397748  |                 0 | True      |
| manual_test\unknown\real\flower.png    | real         |     0.0857541 |                 0 | True      |
| manual_test\unknown\real\outdoor.png   | real         |     0.0737608 |                 0 | True      |
| manual_test\unknown\real\room.png      | real         |     0.0712825 |                 0 | True      |
| manual_test\unknown\real\selfie.png    | real         |     0.0964768 |                 0 | True      |
| manual_test\unknown\screen\laptop.png  | screen       |     0.293419  |                 0 | False     |
