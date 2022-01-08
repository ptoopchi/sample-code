This is a recommendation system for movies. This is a hybrid recommendation system consisting of a content-based and user-based recommendation system. Each model creates a prediction, and then a weighted average is taken as a final output. 

Initial results show that the MSE value for:
- User-based collaborative filtering = 0.9939
- Content-based model = 0.8065
- Hybrid model = 0.3707

The weighting of the Hybrid model is 0.4 for user-based CF and 0.6 for content-based RS.
