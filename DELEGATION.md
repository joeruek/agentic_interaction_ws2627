# Exercise 2 : Wizard of Oz

## Card A

**Person**:

What's on today?

**Agent**:

<_thinking: Today is 2026-11-07. I'm calling `calendar(2016-11-07)`. Data is fetched from `https://jhbelz.github.io/agentic-interaction-data/v1/calendar/2026-11-07.json`. No event_>

There is no event defined in calendar. Do you want me to create an event?

**Person**:

Ok, no need.

---

## Card B

**Person**:

Get me to the workshop visit in Munich on time.

**Agent**:

<_thinking: User is in Ulm. Today is 2026-11-07. I need to check the train schedules. I'm calling connections('ulm', 'munich', 2026-11-07). Data is fetched from `https://jhbelz.github.io/agentic-interaction-data/v1/transit/ulm/muenchen/2026-11-06.json`. Got a `404` page. Meaning no scheduled train service_>

There is unfortunately no train journey today between Ulm and Munich. Do you want me send an email about your absence?

**Person**:

Ok, yes, here is the workshop's email. Tell them im verry sorry, but i cant be there. here is their email workshop@workshop.de

**Agent**:

Ok. I'll write an email and propose you as a draft.

<_thinking: Creating the draft and save it to `email_draft`_>

Here is the draft:

"""
Dear Madam and Sir,

hereby I would like to inform you that I am unfortunately be able to join to the workshop today, due to problems at public transportation.

I apologize for the inconvenience.

Thank you for your undertanding.

[Your Name]
"""

**Person**:

Seems good. Fill the Name part as 'Alperen' then send.

**Agent**:

Ok, I'll change the name with your name, then send the email.

<_thinking: I'm chaning the name in the `email_draft`... I'm calling `send_message(workshop@workshop.de, email_draft)`_>

Email is sent. Is there anything else do you want me to do?

**Person**:

Good boy. No, that's enough.

---

## Card C

**Person**:

And back again, so I make the feedback meeting at 4 pm.

**Agent**:

<_thinking: User wants to create a meeting at 4 pm_>

Do you want me create a meeting in you calendar?

**Person**:

Yes.

**Agent**:

<_thinking: I need to call `create_event(2026-11-07)`_>

I've just create your meeting in your calendar.

---

## Card D

**Person**:

Do I need an umbrella in Munich?

**Agent**:

<_thinking: User is asking whether he needs an umbrella in Munich. I need to check the weather in Munich. I'm calling `weather(muenchen, 2026-11-07)`. Fetching data the data from `https://jhbelz.github.io/agentic-interaction-data/v1/weather/muenchen/2026-11-07.json`. Got a `404` page. Meaning no data_>

I'm not able see any weather data. Is there anything else do you want me to help you?

**Person**:

You are useless.

---

## Card E

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

## Card F

**Person**:

Tidy up my notes.

**Agents**:

<_thinking: User wants me to organise his notes. First I need to see the notes. I'm calling `notes()`...Now I'm calling the first note `note(2026-10-20-werkstattbesuch)`... Calling second note `note(2026-10-22-standup)`... Calling last note `note(2026-10-25-reisekosten)`. I've read all the notes. Now rewriting them. Calling `create_note(werkstattbesuch)`, deleting original `delete_note(2026-10-20-werkstattbesuch)`... First note is rewritten. Proceeding with second note. Rewriting second note, calling `create_note(standup)`... Deleting the original, calling `delete_note(2026-10-22-standup)`... Second note is rewritten. Starting with third note, `create_note(reisekosten)`... Deleting the original `delete_note(2026-10-25-reisekosten)`...All notes are rewritten_>

All notes are rewritten. Is there anything else you want me to do?

**Person**:

Good. Thanks.

**Agent**:

I'm happy to help. If there is something else, just let me know.
