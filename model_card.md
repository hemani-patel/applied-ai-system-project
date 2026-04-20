# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Guessing your music taste

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

This recommender suggests 5 songs from a dataset of 20 songs based on the inputted genre, mood, and energy level. It assumes that the user already knows what they like and can descibe it in a few words. It does not learn from the users listening history or adapt over time. This is built for classroom explorations as each recoomendation is based on how closely a songs feature matches what the user wanted. 

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The system which i implemented checks 4 things. 
1. does the song genre match what the user favorite genre is? if it does it gets +2 points (laregest reward in the system)
2. does the mood match the user wants? If so +1 point
3. how close is the songs energy to user preference? a match gets +1.5 points, and the score decreases he further it gets from the value
4. does the songs acoustic texture match the user preference? if so +1 point

each song gets all of these checks. the max any song can get is 4.5 points, the min is. 0 points. The main change from the starer code was adding the enerfy and acousticness proximity math. The system checks if the score is close enough to the target. 


## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The catalog has 20 songs. The orig8inal had 10 songs but I added 10 more to increase dataset. The cataglog has 17 genres, moods range from happy and chill to angry and melancholy. Each song has 10 attributes: title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. The catalog is biased towards westen genres, there is no diversity in music genres such as afrobeats. Taste that comes from language, culture, or personal memory is invisible to this system.


## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works best when teh user preferences align perfectly with the catalog. The energy proximity math also works the way it should as songs that are slightly off still rank reasonably and the slidong scale is more realistic than a hard cutoff. The system is also fairly easy to explain . For each reccomendation you can see exactly why it ranked where it did. 

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

One weakness I discovered during my experiment is energy and acousticness are correlated, thus they can double penelize certain users. The features are basically opposite in this context so high energy means low acoustic. This means that a user who wants high energy and likes acousticeness gets penelized on both features by every high energy song because no song can satisfy both of these requirements. This limitation was recognized throigh the "acousting headbanger" edge case.

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested 8 profiles. In the standard profiles I evaluated high energy pop, chill lofi, deep intesnse rock, and late night soul. 

High-Energy Pop — expected Sunrise City and Gym Hero to dominate. They did.
Chill Lofi — expected Focus Flow at #1 due to genre + mood + energy match. It scored 4.49/4.50 and ranked first as predicted.
Deep Intense Rock — Storm Runner won cleanly. Blackout Riff (metal) appeared in the top 3 based on energy proximity alone, even without a genre match.
Late-Night Soul — Sunday Soul ranked first. Coffee Shop Stories (jazz) and Twelve Bar Heartache (blues) surfaced as #2 and #3 based on acousticness and energy despite genre mismatches.

In the edge case profiles I tested sad workout, unknown genre, acoustic headbanger, and genre trap. The Genre Trap result was the most unexpected. A song that is numerically the worst match in its genre can still rank first because the +2.0 genre bonus outweighs the combined energy and acousticness penalties. A user receives a recommendation that is factually the worst fit because no other song shares that genre label. The mood sensitivity test showed how much one feature was impacting. When mood was commented out and its weight redistributed, the Chill Lofi rankings barely changed in order. However, Focus Flow's margin over Library Rain decreased from 1.0 point to near 0. Mood was the only thing meaningfully separating two otherwise nearly identical songs.

## comparing differences between outputs

High-Energy Pop vs. Chill Lofi: 
These profiles dont share any of the 5 songs in their top reccomendations but this makes sense. I think the gym hero song keeps showing up for happy pop because both are labeled pop with high energy but the system can't tell a workout song from a feel good song until mood scoring is turned back on.

Deep Intense Rock vs. Late-Night Soul:
Rock produces more loud and electric songs. Soul pulls more warm and mid tempo songs. I think jazz songs come into the top 5 for soul songs becauyse their numbers look simialr to soul songs and the system can't hear the difference. 

Sad Workout vs. Acoustic Headbanger:
These ask for things which can not happen in this dataset,  high energy + sad mood, or high energy + acoustic texture. The system can't notice the contradiction and then returns the least worst option.


Genre Trap vs. Unknown Genre:
In genre trap Drop Zone is the top song for a user who wants something acoustuc and quiet because the genre label EDM matched and the +2 bonous was too large to overcome. 


## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

The largest improvement I would have would be to have a larger catalog with around 200 songs so that it could be more representative. Also, the system could warn you if it couldnt find a song in your genre. Right now it just return whatever is closest. A message would make it more clear and honest to users. Also, i would include more diversity in songs as the top 5 songs are very simialr to each other and a future iteration could enforce one song per genre in the top results. 

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

From this project I learned how much work goes into a reccomendation system to get accurate results. You have to do feature selecttion, weight them, and figure out what to do if preferences conflict with each other. The most surprising this was how much the genre label controled the results, one number was enough to override alll other features. This project also made me think abut apps like Spotify differently. When a reccomended song feels wrong its probably not random. Some feature is being weighted too heavily or a prefernce I have is not being represented in the formula.

