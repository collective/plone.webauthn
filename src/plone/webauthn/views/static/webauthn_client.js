const log_el = document.getElementById('log');

function log(...messages) {
  console.log(...messages);
  log_el.innerText += '\n' + messages.map(m => JSON.stringify(m, null, 2)).join(' ');
}

function error(message) {
  console.error(message);
  log_el.innerText += '\n' + message;
  throw Error('got error:' + message);
}

const asArrayBuffer = v => Uint8Array.from(atob(v.replace(/_/g, '/').replace(/-/g, '+')), c => c.charCodeAt(0));
const asBase64 = ab => btoa(String.fromCharCode(...new Uint8Array(ab)));

async function getPublicKey(path, element, attestation_type, authenticator_type) {
  const user_id = document.getElementById(element).value;

  const r = await fetch(`/Plone/${path}?user_id=${user_id}&attestation_type=${attestation_type}&authenticator_type=${authenticator_type}`);
  
  if(r.status == 404){
    error("User Not Found");
  }

  if (r.status !== 200) {
    error(`Unexpected response ${r.status}: ${await r.text()}`);
  }
  return await r.json();
}

async function post(path, element, creds, challenge) {
  
  const user_id = document.getElementById(element).value;

  const {attestationObject, clientDataJSON, signature, authenticatorData} = creds.response;

  console.log(challenge);
  
  const data = {
    id: creds.id,
    raw_id: asBase64(creds.rawId),
    response: {
      attestationObject: asBase64(attestationObject),
      clientDataJSON: asBase64(clientDataJSON),
    },
    challenge: challenge
  };

  
  if (signature) {
    data.response.signature = asBase64(signature);
    data.response.authenticatorData = asBase64(authenticatorData);
  }
  const r2 = await fetch(`Plone/${path}?user_id=${user_id}`, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {'content-type': 'application/json'}
  });
  if (r2.status !== 200) {
    error(`Unexpected response ${r2.status}: ${await r2.text()}`);
  }
}

async function register() {
  let attestation_type = document.getElementById("select-attestation");
  let authenticatior_type = document.getElementById("select-authenticator");
  const publicKey = await getPublicKey('get-registration-options', 'user_id', attestation_type.value, authenticatior_type.value);
  
  if ( 'error' in publicKey){
    alert(publicKey.error);
    return;
  }

  console.log('register get response:', publicKey);
  
  publicKey.user.id = asArrayBuffer(publicKey.user.id);
  publicKey.challenge = asArrayBuffer(publicKey.challenge);
  
  let creds;

  publicKey["pubKeyCredParams"] = publicKey["pub_key_cred_params"]
  publicKey["user"]["displayName"] = publicKey["user"]["display_name"]
  
  try {
      creds = await navigator.credentials.create({publicKey});
  } catch (err) {
    log('refused:', err.toString());
    return
  }

  await post('add-device', 'user_id', creds, publicKey["expected_challenge"]);

  log('registration successful');
}

async function authenticator() {
  let attestation_type = document.getElementById("select-attestation");
  let authenticatior_type = document.getElementById("select-authenticator");

  const publicKey = await getPublicKey('get-authentication-options', 'user_id', attestation_type.value, authenticatior_type.value);

  if ( 'error' in publicKey){
    alert(publicKey.error);
    return;
  }

  console.log('auth get response:', publicKey);

  publicKey.challenge = asArrayBuffer(publicKey.challenge);
  publicKey.allow_credentials[0].id = asArrayBuffer(publicKey.allow_credentials[0].id);
  delete publicKey.allow_credentials[0].transports;
  
  let creds;
  try {
      creds = await navigator.credentials.get({publicKey: publicKey});
  } catch (err) {
    log('refused:', err.toString());
    return
  }
  await post('verify-device', 'user_id', creds, publicKey["expected_challenge"]);

  log('authentication successful');
}