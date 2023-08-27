===============================
Google Summer Code Final Report
===============================

Project Description
--------------------
  Adding WebAuthn Support for Plone CMS by creating an AddOn for Plone that works as Pluggable Authentication as a Service.

My Contribution
----------------
  Developed an Addon With the following Features:

  i. Logged users can register a new device using weabauthn credentials.

  ii. User can delete the registered webauthn credentials.

  iii. The user can authenticate himself using the registered device and webauthn credential

  iv. All the above functionalities can be accessed through user-facing UI in Plone classical UI

  v. Created dedicated forms/dialogues for registration and authentication

  vi. Added links from standard login dialogue to login with webauthn

The current state
------------------
  The current state of the project is working as expected and the user created through add users page can log in using the password to register his first device and then use the webauthn credentials to log in later. Users can register or delete the credentials whenever they want.

What's left to do?
-------------------
  Need to make passwords optional and add a Recover Account feature here https://docs.google.com/document/d/1C042vaqj3TZEx_zHeutpZuGrVZyLLiEMIiY4d6Kw5pk/edit?usp=sharing

Challenges
----------
  One of the challenges I faced was understanding the workings of Plone's existing authentication flow to add webauthn into it which took the most time of the project and learned a lot of new things.
