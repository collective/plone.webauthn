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

Current Project
----------------
  The current project is a Pluggable Authentication Service which will be used by existing plone authentication to authenticate the user using webauthn credentials.  When logging in using webauthn login page a post request with username, webauthn credential data and some other required data is sent to Plone Login. From where Plone authentication It tries to validate the request with all available PAS’s in Plone which are enabled for the site and plone.webauthn is one such PAS which can validate the users with username and webauthn credentials. If validated successfully user will be redirected to Plone default home page. 
  In the scenario when the user loses a registered device he can just login into his plone account using his plone username and credentials and then access key-management page to register a new device and or the credentials of the lost device.

Why are we still using passwords?
---------------------------------
  The actual proposal was the configuration option for the Admin to choose between webauthn as the primary authentication or secondary authentication. When used as a primary authentication a feature called Recovery Codes was proposed to access the account once to register a new device. But this cannot be implemented with just PAS and we need to change existing Plone Authentication which itself is project that needs more time than GSOC period. When changing the existing plone authentication we also need inputs from plone foundation about the policies that needs to be implemented when dealing with no password sites.
	
Future Plone Authentication
----------------------------
	The Current Plone Authentication is outdated and needs to be changed to a customizable feature by admin where he can choose between combinations of password and webauthn methods. To do this we have make changes to authentication flow but at the same also needs to take care assigning roles, groups and permissions as we do in the existing authentication. This is a big project and will need efforts from multiple people to take care different PAS option we are using as of now. The policies for clients that use the plone will also need to be updated according the password less authentication standards as the security will be moved from server storage ability to user personal devices security.

Recovery Codes
---------------
	Once the above mentioned changes are implemented we also need to implement Recovery Codes feature which are bunch of one time use codes generated when the user registers for the first time and can be used to access their account and add or delete a webauthn credentials. These Recovery Codes will be stored in the database after they are encrypted and will be decrypted before used for validation.


Implementation
---------------
	Implemeting Recovery Codes straight forward but the critical part is the encryption we can use symmetric and asymmetric encryption. The server creates a asymmetric public and private key and shares the public key to client. The client then creates a symmetric key and encrypts the recovery code with that. Then the symmetric key is encrypted with the public key from server and the encrypted symmetric key and encrypted Recovery code is sent to server where servers private key is used to decrypt the symmetric key from client and then later used to decrypt the recovery code. Using the decrypted Recovery Code a Hash code will be generated using a SHA algorithm and the hashcode is saved in database.
	Later when user uses the recovery code we use the same hash code algorithm to generate the hashcode which will be validated with hashcode saved in database.

Why is it Less Secure?
----------------------
  Ultimately this is still not a secure way because we are storing some kind of secret which will again be open to security attacks. We can aslo consider the same recovery codes option that will be generated and sent to user like one time passwords through their mail or mobile numbers.


Challenges
----------
  One of the challenges I faced was understanding the workings of Plone's existing authentication flow to add webauthn into it which took the most time of the project and learned a lot of new things.
