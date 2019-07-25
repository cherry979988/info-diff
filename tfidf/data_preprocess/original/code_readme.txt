1. PSM
====Introduction====
Use the method of propersity score matching to test the influence on retweet behaviors from the friends. The basic idea is to first fix users in the treatment group as those who have more than one followee retweeted a given message, and then for each user in the treatment group, we try to find the most matched user from the original control group, and finally construct a new control group by all the matched users. 

When processing the raw data, for each user who has retweeted a message, we view her as active at the specific time span when she retweeted, and we also treat her as inactive instances at other time spans before she really retweeted. For each follower of an active user, we treat her as an inactive instance at every time span. Then we count the number of previous active neighbors for each active and inactive instance. Finally, we can determine the instances in the treatment and control group. Please refer to the details in the paper.


======Input=========
1.Following network
2.Retweet behavior data
3.User profile
4.User2id map

======Output========
Six files represent the outputs in 0-1, 1-5,5-10,10-24,24-48,48-72 hour respectively.
In each file:
One line represents the outputs for one message. 
One line contains several quads. 
In each quad (num1, num2, num3, num4), num1 is the number of followees retweeted the message before for the users in the treatment group, num2 is the number of users in treatment group or control group(they are the same), num3 is the number of users who retweeted the message in the treatment group, num4 is the number of users who retweeted the message in the control group.

======Code explanation========
run PSM.cpp 



2. PairwiseInfluence
====Introduction====
Stat retweet probability when varying the average pairwise influence and sum pairwise influence from the followees.
The process of active and inactive instances is the same as PSM.


=====Input=======
1)Following network. Each edge is associated with a score representing the relatedness between two nodes. The relatedness is calculated by using random walk with restart. You can run RandomWalkWithRestart.cpp by using the following network as input.  
2)Retweet behavior data

=====Output==========
1)the retweet probability conditioned on the average pairwise influence from friends.
One line is the probability for each value of average pairwise influence.
The average pairwise influence varies from 0.1 to 1.0 with 0.05 as interval.
2)the retweet probability conditioned on the sum pairwise influence from friends.
One line is the probability for each value of sum pairwise influence.
The sum pairwise influence varies from 1 to 20 with 1 as interval.

====Code explanation=========
1)run RandomWalkWithRestart.cpp
2)run PairwiseInfluenceMain.cpp


3. StructureInfluence
====Introduction====
Stat retweet probability when varying the number of circles formed by the active neighbors for each given the number active neighbors.
The process of active and inactive instances is the same as PSM.


=====Input=======
1)Following network. 
2)The file indicates for each user, the ego circle each of her followees belongs to. The file can be obtained by executing the program get_block.cpp, which takes the following network as input. 
3)Retweet behavior data

=====Output==========
Seven files represents the retweet probabilties conditioned on different number of circles for the given 2,3,4,5, 10, 20,30 active neighbors respectively.
In each file, each line contains a quad(num1, num2, num3, num4), where num1 is the number of circles formed the active neighobrs, num2 is the number of users who retweeted the message, num3 the total number of users, num4 equals num2/num3.


====Code explanation=========
1)run get_block.cpp.cpp
2)run prob_set_sizefix.cpp

4. Training&Test
====Introduction====
Conduct logistic regression to predict the retweet behaviors by using the influence locality features or several baseline features.

=====Process=======
1)run RandomWalkWithRestart.cpp
	Introduction: use random walk with restart to measure the relatedness between any two nodes in a graph
	Input: following network
	Output: the same network with each edge associated with a relatedness score.
2)run LDA
	Introduction: use LDA to calculate the probability of each tweet belongs to each topic.
	Input: the orginial tweet content
	Output: the tweet-topic probabilities
3)run generate_author_topics.py
	Introduction: calculate the the probablity of the user belongs to each topic by averaging the probabilities of all the tweets an user publishes/retweets belongs to each topic.
	Input: the tweet-topic probabilities and retweet behavior data
	Ouput: the user-topic probailities
4)run GenerateInstance.cpp
	Introduction: generate positive and negative instances from raw data
	Input: the following network, the retweet behavior data, the user profile and the user2id map.
	Output: instances.txt, with each instance contains six lines.
   Line1: user_id, label(active/inactive), the nubmer of reciprocal friends, the number of followers, the number of followees, the number of published/retweeted tweets, gender, verification status, the similarity between the user and the original message (calculate the Jensen-Shannon divergence between the topic distribution of a user and the topic distribution of a message), the elapsed time from when the original message is published.
   Line2: the number of followees who retweeted the same message before.
   Line3: the number of circles formed by the followees who retweeted the same message before
   Line4: the ids of followees who retweeted the same message before.
   Line5: indicate the social tie to each followee who retweeted the same message before is reciprocal(1) or parasocial(0) .
   Line6: for each followee who retweeted the same message before, indicate the difference between the time when the followee retweeted the message and the time when we try to predict current user's retweet behavior.
5)run GenerateFeatures.cpp
	Introduction: generate features for each instance based on different influence locality functions. Please refer to Table 3 in our paper for the function details.
	Input: instances.txt and a following network with each edge associated with a score calculated by Random Walk With Restart.
	Output: A file (ins.txt) for training and test, wich each line representing a postive instance (begin with 1) or a negative instance (begin with 0).
6)run LogisticRegression.bat
  Introduction: use logistic regression model to train a classifier for predicting retweet behaviors
  Input: ins.txt
  Output: log.txt includes accuracy, precision, recall, F1 and coefficients for all the features. res.txt includes the true label and the predicted probability.


