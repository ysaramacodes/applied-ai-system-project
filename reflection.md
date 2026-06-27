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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
