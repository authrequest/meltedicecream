const crypto = require("crypto");
const store = require("./store");
const request = require('request-promise');
const {machineId, machineIdSync} = require('node-machine-id');

function pad(k, n) {
  k = k.toString();
  while (k.length < n) {
    k = "0" + k;
  }
  return k;
}

class License {
  static hwid() {
    var hwid =  machineIdSync();
    return hwid;
  }

  static info() {
    const license = store.get("key", "licensing");
    if (!license) return { active: false };

    return {
      name: license.first + " " + license.last,
      created: license.created,
      active: true,
      expiry: license.expiry,
      key: license.key
    };
  }

  static async check() {

    const secret = License.hwid();
    const res = await request('http://68.183.117.132:8080/keys/check', {
        resolveWithFullResponse: true,
        simple: false,
        method: 'POST',
        json: {
            secret
        }
    });
    
    const active = res.statusCode == 200;
    if(!active) return store.set('key', null, 'licensing');

  }

  static async redeem(key) {
    
    const secret = License.hwid();
    const res = await request('http://68.183.117.132:8080/keys/redeem', {
        method: 'post',
        resolveWithFullResponse: true,
        simple: false,
        json: {
            key, secret
        }
    });

    if(res.statusCode != 200) return false;

    store.set("licensedBefore", true, "licensing");
    return store.set(
      "key",
      {
        key,
        active: true,
        created: new Date(),
        expiry: new Date(parseInt(res.body.expires))
      },
      "licensing"
    );
  }

  static firstTime() {
    return store.get("licensedBefore", "licensing") != 1;
  }
}

module.exports = License;