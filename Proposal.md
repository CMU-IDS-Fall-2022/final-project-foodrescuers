# Final Project Proposal

**GitHub Repo URL**: (https://github.com/CMU-IDS-Fall-2022/final-project-foodrescuers)

**Team**: Durvesh Vilas Malpure, Michael Van Buren, Neha Nishikant, Uyen Tran, & Abubakir Siedahmed

## How can we apply modern data science tools to help reduce food waste?

According to the United States Department of Agriculture (USDA), between 30 - 40 percent of the food supply in the US is wasted. This corresponds to about 133 billion pounds and $161 billion worth of food in 2010. This is not just a problem in the United States; one-third of food produced for human consumption is lost or wasted globally. This amounts to 1.3 billion tons annually, worth approximately $1 trillion. If wasted food were a country, it would be the world's third-largest producer of carbon dioxide, after the USA and China (“5 Facts about Food Waste and Hunger | World Food Programme”). We’d like to pose the following question, how can we do our part to best reduce food waste? To answer this question, we will develop an application that will allow people to make conscious decisions about the food they already have to reduce waste. We plan to provide an user interface where the user can input the ingredients they have at home, find popular recipes with those ingredients, and provide the most environmentally friendly dish they can make with their home ingredients. 

We plan to provide the user with visualizations regarding the carbon footprint of the food and the ingredients they consume. Specifically, we would like to show how different ingredients' footprints compare to each other. This part of visualization is a setup for our recipe recommender. To address the food waste problem , we plan to use the Environmental Impacts of Food dataset of the carbon footprint of food ingredients for the EDA section. The dataset includes other unique aspects, such as each ingredient's land and water use. We hope to create appealing and powerful visualizations to convey the gravity of the problem and the cost of food waste. Another type of visualization we would have is to highlight metrics about food waste such as most popular ingredients (provided in the introduction).

Based on the dataset of recipes and food waste, we are planning to use a similarity based model or a recommender system that will try to recommend dishes with a metric/loss that will focus on reducing the waste food. We plan to use features such as perishability, time of buying, expiry date, etc. Based on these models, we would recommend recipes that are possible with the available ingredients than what’s specified in the recipe. Along with this, we will develop a simple model that finds the carbon impact of store-bought foods and suggest what to buy that will be the most environmentally friendly while also trying to be economical. We can define the similarity based on textual embeddings and try to predict the recipe and its impact. We are considering using datasets such as the Recipe1M+ dataset for additional tasks.

Since our project aims to reduce the amount of food waste one person at a time, we will inform users of how much they’re saving and how much they will save. We believe that providing the user with a concrete number could motivate users to continue using our system. To calculate the waste avoided, we plan to sum the waste avoided for each ingredient which can be found by multiplying the carbon footprint of an ingredient per 100 grams. Once we have that, then we can calculate the waste avoided by the amount of that ingredient in the recipe. Lastly, we’ll forecast to the user the amount of waste avoided over a period of time depending on how often the user makes the dishes.


**Citations**: \
How we fight food waste in the US. Feeding America. (n.d.). Retrieved October 31, 2022, from https://www.feedingamerica.org/our-work/our-approach/reduce-food-waste \
“5 Facts about Food Waste and Hunger | World Food Programme.” Wfp.org, 2 June 2020, www.wfp.org/stories/5-facts-about-food-waste-and-hunger. Accessed 1 Nov. 2022. \
Recipe1M+: A Dataset for Learning Cross-Modal Embeddings for Cooking Recipes and Food Images, http://pic2recipe.csail.mit.edu/
“Data Explorer: Environmental Impacts of Food.” Our World in Data, Global Change Data Lab, 2018, https://ourworldindata.org/explorers/food-footprints. 

\

# Sketches and Data Analysis

## Data Processing

## System Design

