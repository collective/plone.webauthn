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

async function getPublicKey(path, user_id, cname) {
  
    const r = await fetch(`/Plone3/${path}?user_id=${user_id}&cname=${cname}`);
    
    if(r.status == 404){
      error("User Not Found");
    }
  
    if (r.status !== 200) {
      error(`Unexpected response ${r.status}: ${await r.text()}`);
    }
    return await r.json();
}

async function post(path, creds, challenge, user_id, cname) {

    const {attestationObject, clientDataJSON, signature, authenticatorData} = creds.response;
    
    const data = {
      user_id: user_id,
      cname: cname,
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

    const r2 = await fetch(`Plone3/login`, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {'content-type': 'application/json'}
    });
    console.log(r2);
    if (r2.status !== 200) {
      error(`Unexpected response ${r2.status}: ${await r2.text()}`);
    }
}


async function authenticator(user_id, cname) {
  
    const publicKey = await getPublicKey('get-authentication-options-for-login', user_id, cname);
  
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
    await post('verify-device-for-login', creds, publicKey["expected_challenge"], user_id, cname);
  
    log('authentication successful');
}


