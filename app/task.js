const spawn = require('child_process').spawn;
const path = require('path');
const { EventEmitter } = require('events');
const License = require('./license');
const { ipcMain, app } = require('electron');
const fs = require('fs');

class Task extends EventEmitter {

    constructor(profile) {
        super()

        this.secret = License.hwid();
        
        const {
            email,
            firstname,
            lastname,
            address1,
            address2,
            zip,
            city,
            state,
            phone,
            card,
            expMM,
            expYYYY,
            cvv,
            size,
            keyword,
            category,
            color,
            proxy
        } = profile;

        this.config = [
            email,
            firstname,
            lastname,
            `${firstname} ${lastname}`,
            address1,
            address2,
            zip,
            city,
            state,
            phone,
            card,
            expMM,
            expYYYY,
            cvv,
            size,
            keyword,
            category,
            color,
            proxy
        ];

        this.profile = profile;

        this.process = null;

        this.percent = 0;
        this.status = 'idle';

        this._receive = this._receive.bind(this);
        this.start = this.start.bind(this);
        this.stop = this.stop.bind(this);
    }

    _receive(data) {
        data = data.toString().trim();
        fs.appendFileSync(
            path.resolve(app.getPath('userData'), './python.log'),
            `TASKID[${this.id || -1}]: ${data}\n`
        )

        data = data.split('<<');

        const payload = {
            command: data[0],
            args: data.slice(1)
        }

        switch(payload.command) {

            case 'launch':
                console.log('Python started with data: ', payload.args[0]);
                this.status = 'running';
                this.error = null

                this.emit('start');
                break;
            case 'progress':
                let percent = parseInt(payload.args[0]);
                if(isNaN(percent)) {
                    throw 'bad output'
                }

                this.emit('progress', percent);
                this.percent = percent;
                break;
            case 'error':
                console.log('Error!', payload.args[0] || 'unknown!');
                this.error = payload.args[0];
                this.status = 'error';
                this.emit('error', payload.args[0])
                this.stop(1);
                break;
            case 'captcha':
                ipcMain.once('got captcha', (cap) => {
                    console.log(cap)
                    this.process.stdin.write(cap + '\n');
                })
                if(!global.winMainCap) {
                    return;
                }
                global.winMainCap.webContents.send('need captcha')

        }
    }

    start() {
        console.log("Python secret:", this.secret);
        const file = path.resolve(__dirname, process.platform == 'win32' ? '../static/supremeRef.exe' : '../static/supremeRef');
        this.process = spawn(file, [process.port, this.secret, this.config.join(',') ]);
        this.process.stdout.on('data', this._receive);
        this.process.stderr.on('data', this._receive);
        this.process.on('close', () => this.process = null);
        this.status = 'running';
    }

    stop(fail = 0) {
        if(this.process != null)
            this.process.kill(9);
        this.percent = 0;
        this.emit('stop')
        this.status = fail ? 'error' : 'idle';
    }

}

module.exports = Task;

// const T = new Task([
//     'some_email@mailinator.com',
//     'firstname',
//     'lastname',
//     'fullname',
//     '4709 Brabant way',
//     'Elk Grove CA',
//     '95757',
//     'Elk Grove',
//     'CA',
//     '2078483726',
//     '1234567891234567',
//     '12',
//     '2010',
//     '102',
//     'large',
//     'Bag',
//     'Bags',
//     'Black',
//     ''
// ]);

// T.start()

// setInterval(() => console.log(T.percent), 1000)