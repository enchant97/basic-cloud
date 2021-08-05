import * as api_types from "./types.js";

export default class BasicCloudWsApi {
    static bearer_token;
    static base_url = window.location.origin.replace("http", "ws");
    static websocket;
    /**
     * create a new websocket connection to api server
     * @returns the websocket object
     */
    static ws_connect() {
        BasicCloudWsApi.websocket = new WebSocket(
            BasicCloudWsApi.base_url + "/api/ws?bearer_token=" + BasicCloudWsApi.bearer_token);
        return BasicCloudWsApi.websocket;
    }
    /**
     * mark the websocket as finished (close websocket)
     */
    static ws_finished() {
        if (BasicCloudWsApi.websocket) {
            BasicCloudWsApi.websocket.close();
        }
        BasicCloudWsApi.websocket = null;
    }
    /**
     * send a websocket message with a payload
     * @param {api_types.WS_MESSAGE_RECEIVE_TYPES} message_type - the message type
     * @param {object} payload - the payload
     * @param {Date} when - when it happened
     */
    static send_message(message_type, payload, when = null) {
        if (when === null) { when = new Date(); }
        let message = {
            message_type,
            when,
            payload,
        };
        // XXX this is a patch for pythons date-time to iso
        message.when = message.when.toISOString().replace("Z", "");
        BasicCloudWsApi.websocket.send(JSON.stringify(message));
    }
    /**
     * send a move directory message
     * @param {string} directory - the directory
     */
    static send_move_directory(directory) {
        let payload = { directory };
        BasicCloudWsApi.send_message(
            api_types.WS_MESSAGE_RECEIVE_TYPES.DIRECTORY_CHANGE,
            payload
        );
    }
}
