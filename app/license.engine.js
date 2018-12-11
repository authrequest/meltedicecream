const net = require('net');
const store = require('./store');

class License {

    static info() {
        return new Promise((resolve, reject) => {
            const request = new net.Socket();
            request.on('data', data => {
                const parsed = data.split('>>');
                let payload = parsed[1];
                payload = payload.split(',');
                const name = payload[0];
                const created = payload[1];
                const expiry = payload[2];
                const active = new Date(expiry) > new Date();
                return resolve({ name, created, expiry, active });
            });

            request.on('close', reject);
            request.on('error', reject);
            request.connect();
            request.write(`KEY_INFO`);
            return setTimeout(reject, 10000);
        })
    }

    static redeem(key, first, last) {
        return new Promise((resolve, reject) => {
            const request = new net.Socket();
            request.on('data', resolve);
            request.on('close', reject);
            request.on('error', reject);
            request.connect();
            request.write(`KEY_REDEEM>>${ [ key, first, last ].join(',') }`);
            return setTimeout(reject, 10000);
        })
    }

    static firstTime() {
        console.log(store.get('licensedBefore', 'licensing') != 1)
        return store.get('licensedBefore', 'licensing') != 1;
    }

}

module.exports = License;