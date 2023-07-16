const log_el = document.getElementById('log');

function log(...messages) {
  log_el.innerText += '\n' + messages.map(m => JSON.stringify(m, null, 2)).join(' ');
}

function error(message) {
  console.error(message);
  log_el.innerText += '\n' + message;
  throw Error('got error:' + message);
}

const asArrayBuffer = v => Uint8Array.from(atob(v.replace(/_/g, '/').replace(/-/g, '+')), c => c.charCodeAt(0));
const asBase64 = ab => btoa(String.fromCharCode(...new Uint8Array(ab)));

async function getPublicKey(path, attestation_type, authenticator_type) {

  cname = document.getElementById("cname").value;

  const r = await fetch(`/Plone3/${path}?cname=${cname}&attestation_type=${attestation_type}&authenticator_type=${authenticator_type}`);
  console.log(r);
  if(r.status == 404){
    error("User Not Found");
  }

  if (r.status !== 200) {
    error(`Unexpected response ${r.status}: ${await r.text()}`);
  }
  return await r.json();
}

async function post(path, creds, challenge) {

  const {attestationObject, clientDataJSON, signature, authenticatorData} = creds.response;
  
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
  cname = document.getElementById("cname").value;
  const r2 = await fetch(`Plone3/${path}?cname=${cname}`, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {'content-type': 'application/json'}
  });
  if (r2.status !== 200) {
    error(`Unexpected response ${r2.status}: ${await r2.text()}`);
  }
  console.log(r2);
}

async function register() {
  let attestation_type = document.getElementById("select-attestation");
  let authenticatior_type = document.getElementById("select-authenticator");
  const publicKey = await getPublicKey('get-registration-options', attestation_type.value, authenticatior_type.value);
  
  if ( 'error' in publicKey){
    alert(publicKey.error);
    return;
  }

  //console.log('register get response:', publicKey);
  
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

  await post('add-device', creds, publicKey["expected_challenge"]);

  log('registration successful');
  getKeys();
}

async function authenticator() {
  let attestation_type = document.getElementById("select-attestation");
  let authenticatior_type = document.getElementById("select-authenticator");

  const publicKey = await getPublicKey('get-authentication-options', attestation_type.value, authenticatior_type.value);

  if ( 'error' in publicKey){
    alert(publicKey.error);
    return;
  }

  publicKey.challenge = asArrayBuffer(publicKey.challenge);
  publicKey.allow_credentials[0].id = asArrayBuffer(publicKey.allow_credentials[0].id);
  delete publicKey.allow_credentials[0].transports;

  //console.log(publicKey);
  
  let creds;
  try {
      creds = await navigator.credentials.get({publicKey: publicKey});
  } catch (err) {
    log('refused:', err.toString());
    return
  }
  await post('verify-device', creds, publicKey["expected_challenge"]);

  log('authentication successful');
}