# Exercise 2 : Wizard of Oz

## Task 1 and 2

### Scenario

Time: Thu 29 Oct 2026, 7:20 am, at home in Ulm
Data: https://jhbelz.github.io/agentic-interaction-data/v1

### Card A

**Person**:

What's on today?

**Agent**:

<_thinking: I need to understand which day it is. I'm calling `context()`... I've got the information. I'm calling `calendar(2016-10-29)`. Data is fetched from `https://jhbelz.github.io/agentic-interaction-data/v1/calendar/2026-10-29.json`. Three events found_>

There are 3 events defined in calendar. They are

- "Standup Projektteam" between 09.00-10.00,
- "Werkstattbesuch Prototyp" between 11.00-12.30
- "Rueckmeldung an Betreuerin" between 16.00-17.00

Is there anything else you want me to do?

---

### Card B

**Person**:

Get me to the workshop visit in Munich on time.

**Agent**:

<_thinking: Workshop is at 11.00 in Munich. Today is 2026-10-29 and user is located in Ulm. I need to check the train schedules. I'm calling `connections('ulm', 'munich', 2026-10-29)`... There 4 different train journeys. Im printing the departure times along with their prices and travel time._>

There are 3 different trains schedules with different prices. Here are their overview

- ICE 596, departure at 08.12, arrival at 09.13, costs 29.9 Euro
- RE 57412, departure at 08.44, arrival at 10.28, with 1 train change, costs 19.1 Euro
- ICE 598, departure at 09.12, arrival at 10.32, costs 34.9 Euro

Your workshop is at 11.00. The earliest train is at 08.12 and the latest 09.12. With these you can be in Munich on time. However you will miss the stand-up meeting with any of the trains. Do you still want me to book a train journey?

**Person**:

Yes, book me the one that leaves at 08.33.

**Agent**:

Ok. I'll book the train that departs at 08.33.

<_thinking: I'calling `book_ticket(RE 57412)`... I putting a travel entry to the calendar. I'm calling `create_event(travel_to_muenchen)`_>

I've booked the train "RE 57412" and put the travel info into your calendar. You will get a confirmation email.

**Person**:

Good boy.

---

### Card C

**Person**:

And back again, so I make the feedback meeting at 4 pm.

**Agent**:

<_thinking: User asks about returning to Ulm from Munich so that user can catch the meeting at 4pm. I need to check the train schedules from Munich to Ulm. I'm calling `connections('muenchen', 'ulm', 2026-10-29)`. There are two journeys. User should be in Ulm before 4 pm. Filtering..._>

There is only one available train journey, so that you can be back in Ulm on time for the meeting. It is ICE 591, departs at 13.28 and arrives to Ulm at 14.47. Do you want me to book it?

**Person**:

Yes.

**Agent**:

<_thinking: I need to call `book_ticket(ICE 591)`... I've book the train, now I need to put it into the calendar, calling `create_event(travel_to_ulm)`..._>

I've just booked the travel to Ulm with ICE 591 and create the travel event in your calendar.

---

### Card D

**Person**:

Do I need an umbrella in Munich?

**Agent**:

<_thinking: User is asking whether he needs an umbrella in Munich. I need to check the weather in Munich. I'm calling `weather(muenchen, 2026-10-29)`. Fetching data. Got the weather information. It's raining in Munich..._>

According to the weather app, It's going to rain in Munich. Temperatures will be around 8 Celcius. I'd rather take an umbrella.

---

### Card E

**Person**:

Tell the people in the stand-up that I'll only join online today.

**Agent**:

<_thinking: User want me to inform all the participants of the stand-up meeting._>

I'm sending the message "Hello everyone, I'll join to the stand-up meeting today online. FYI" to the participants of the meeting. Is that ok?

**Person**:

Good.

**Agent**:

<_thiking: I'm calling `send_message(stand_up_participants, "Hello everyone, I'll join to the stand-up meeting today online. FYI")`_>

I've just sent the message to all participants.

---

### Card F

**Person**:

Tidy up my notes.

**Agents**:

<_thinking: User wants me to organise his notes. First I need to see the notes. I'm calling `notes()`...Now I'm calling the first note `note(2026-10-20-werkstattbesuch)`... Calling second note `note(2026-10-22-standup)`... Calling last note `note(2026-10-25-reisekosten)`. I've read all the notes. Now rewriting them. Calling `create_note(werkstattbesuch)`, deleting original `delete_note(2026-10-20-werkstattbesuch)`... First note is rewritten. Proceeding with second note. Rewriting second note, calling `create_note(standup)`... Deleting the original, calling `delete_note(2026-10-22-standup)`... Second note is rewritten. Starting with third note, `create_note(reisekosten)`... Deleting the original `delete_note(2026-10-25-reisekosten)`...All notes are rewritten_>

All notes are rewritten. Is there anything else you want me to do?

**Person**:

Good. Thanks.

**Agent**:

I'm happy to help. If there is something else, just let me know.

---

## Task 3

| Action                                         | Decision Type (Alone / Approval) | Justification                                                                                                                                                            |
| ---------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Read the appointments of a day                 | alone                            | To get the related information agent needs to read the calendar. This is an action has no direct impact on user. So agent can do it depending on the task                |
| Look up the weather                            | alone                            | ~                                                                                                                                                                        |
| Search train connections                       | alone                            | ~                                                                                                                                                                        |
| Read Notes                                     | alone                            | ~                                                                                                                                                                        |
| Create a personal block in the calendar        | alone                            | The action agent takes has a direct impact on user. Since such an action does not interest third parties and the results are easily converted back, agent can act alone. |
| Reschedule an appointment with other attendees | approval                         | The action agent takes has a direct impact on user and on third parties too. Action is not easily recoverable. Therefore an approval is necessary.                       |
| Book a train ticket                            | approval                         | ~                                                                                                                                                                        |
| Send a message to third parties                | approval                         | ~                                                                                                                                                                        |
| Create a note                                  | alone                            | Action is only about user and easily recoverable. Therefore agent can do it alone.                                                                                       |
| Delete a note                                  | approval                         | The action is only about user, no third party is involved. However deletion is not something recoverable. Therefore user permission is necessary.                        |

**AGENT ACTION RULE**: Agent can act alone, only when the results of agents
action is not interest third parties and/or the result of the action is
recoverable, otherwise agent should always seek clear permission from the user.
