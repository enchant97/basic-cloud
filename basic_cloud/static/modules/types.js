/**
 * enums responsible for marking
 * how the content has changed
 */
export const CONTENT_CHANGE_TYPES = {
    OTHER_CHANGE: 0,
    CREATION: 1,
    DELETION: 2,
    DOWNLOAD: 3,
    SHARED: 4,
}
/**
 * enums responsible for marking
 * what payload has been sent
 * in a message from the server
 */
export const WS_MESSAGE_SEND_TYPES = {
    WATCHDOG_UPDATE: 1,
}
/**
 * enums responsible for marking
 * what payload has been sent
 * in a message from the client
 */
export const WS_MESSAGE_RECEIVE_TYPES = {
    DIRECTORY_CHANGE: 1,
}
