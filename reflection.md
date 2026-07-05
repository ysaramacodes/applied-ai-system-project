# PawPal+ Project Reflection

## 1. System Design

The three options a user should be able to do is add a pet, schedule a walk and see today's tasks

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
    I created a Pet, Owner, Task and Schedule class. The Pet class responsibilities was ti store the details about the pet. The Owner class holds their contact info of the pet owner incase of an emergency. The Task class handles lifecycle activities. The schedule class creates a schedule based off ther owners availability and pet needs, etc.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
I changed my Task class. In the beginning it had no reference to pets which is wrong because each task belongs to a specific pet as they all have unique needs.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
        
    The constraints my schedule considers is time and preference.

- How did you decide which constraints mattered most?
     I decided that time mattered the most because the pet woner needs to decide what time frame they are available so that the app can generate a schedule based off the information.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

One tradeoff my scheduler makes is that it is simple and faster conflict handling versus a globally optimal scheduling.

- Why is that tradeoff reasonable for this scenario?

The tradeoff is reasonable for this scenario because it keeps the scheduler practical and a full global optimization would require way more code making it less practical, harder to read and it would slow down normal usage for this specific app.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    I used AI for brainstorming and debugging my time conflicts.

- What kinds of prompts or questions were most helpful?

    Explain how this app is supposed to function.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
   
    I did not accept an AI suggestion when it wanted to mark a same-pet time conflict instead of finding a nearby slot with a small buffer.

- How did you evaluate or verify what the AI suggested?

I created pytests based on the AI suggested code and ran my pytest to verify that all my tests passed.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?

I am very confident that my app works because I handled alot of edge cases and I created alot of pytests. I also ran my code and tested my app and I did not notice any error at all.

- What edge cases would you test next if you had more time?
I would test conflict tasks more because what if there is no next available time slot.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with being able to add multiple pets and tasks for each seperate pet.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would add an ability for the user to manually adjust task times after scheduling.
**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that the AI doesn't know wht you are thinking meaning you have to be very specific when using AI because the app would function completely different. 