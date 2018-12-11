const fs = require('fs');
const path = require('path');

const app = require('electron').app;

const DD = path.resolve(app.getPath('userData'), './store');
if(!fs.existsSync(DD))
    fs.mkdirSync(DD);

class Store {

    static get(key, store = 'default') {
        
        try {
            const json = Store.getStore(store);
            const value = key ? json[key] : json;

            return value;
        } catch (e) {
            Store.fixStore(store);
            return null;
        }

    }

    static set(key, value, store = 'default', x = 0) {

        try {
            let storeData = Store.getStore(store);
            storeData[key] = value;
            storeData = JSON.stringify(storeData, null, 4);

            const storeFilePath = path.resolve(DD, store);
            fs.writeFileSync(storeFilePath, storeData);

            return value;
        } catch (e) {
            Store.fixStore(store);
            if(x == 10) return null;
            return Store.set(key, value, store, x + 1);
        }

    }

    static delete(key, store = 'default') {

        try {
            let storeData = Store.getStore(store);
            delete storeData[key];
            storeData = JSON.stringify(key ? storeData : {}, null, 4);

            const storeFilePath = path.resolve(DD, store);
            fs.writeFileSync(storeFilePath, storeData);

            return true;
        } catch (e) {
            Store.fixStore(store);
            return false;
        }

    }

    static getStore(store) {
        const storeFilePath = path.resolve(DD, store);
        const storeFile = fs.readFileSync(storeFilePath).toString();
        return JSON.parse(storeFile);
    }

    static fixStore(store) {
        const storeFilePath = path.resolve(DD, store);
        return fs.writeFileSync(storeFilePath, '{}');
    }

}

module.exports = Store;