const net = require('net');

class Task {

    constructor(config) {
        this._receive = this._receive.bind(this);
        this._close = this._close.bind(this);
        this._error = this._error.bind(this);

        this.closed = false;
        this.config = config;

        this.client = new net.Socket();
        this.client.on('data', this._receive);
        this.client.on('close', this._close);
        this.client.on('error', this._error);

        this.responses = {};
    }

    _receive(data) {
        // parse data
        data = data.split('>>');
        if(data.length === 2) {
            return this._event({
                cmd: data[0],
                payload: data[1]
            });
        }
        const id = data[0];
        const cmd = data[1];
        const payload = data[2];

        this.responses[id] = {
            cmd, payload, time: Date.now()
        };
    }

    _close() {
        this.closed = true;
    }

    _error(e) {
        throw e;
    }

    _event(ev) {
        if(this.onProgress && typeof this.onProgress == 'function')
            this.onProgress(ev);
    }

    _request(command, data = '') {
        return new Promise((resolve, reject) => {

            const self = this;
            let id = Math.floor(Math.random() * 10000);
            let payload = [id, command, data].join('>>');
            this.client.write(payload);
            
            let timer = 0;
            var reqTimeout = setInterval(i => {

                timer++;
                if(timer === 10) {
                    clearInterval(reqTimeout);
                    return reject(new Error('Connection Timeout'));
                }

                if(self.responses[id]) {
                    clearInterval(reqTimeout);
                    return resolve(self.responses[i]);
                }

            }, 1000);
        })
    }

    start() {
        return this._request('LAUNCH', this.getConfig());
    }

    stop() {
        return this._request('STOP');
    }

    progress() {
        return this._request('PROGRESS');
    }

}

module.exports = Task;