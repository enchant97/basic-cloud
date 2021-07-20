/**
 * unhandled http exception
 */
export class UnhandledError {
    constructor(message) {
        this.name = 'UnhandledError';
        this.message = message || '';
        this.stack = (new Error()).stack;
    }
}

/**
 * when access token doesn't work
 */
export class AuthError {
    constructor(message) {
        this.name = 'AuthError';
        this.message = message || '';
        this.stack = (new UnhandledError).stack;
    }
}

/**
 * when server does not understand data given
 */
export class UnprocessableError {
    constructor(message) {
        this.name = 'UnprocessableError';
        this.message = message || '';
        this.stack = (new UnhandledError).stack;
    }
}

/**
 * when server fails
 */
export class InternalServerError {
    constructor(message) {
        this.name = 'InternalServerError';
        this.message = message || '';
        this.stack = (new UnhandledError).stack;
    }
}
