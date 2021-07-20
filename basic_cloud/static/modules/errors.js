/**
 * unhandled http exception
 */
export class UnhandledError {
    constructor(message) {
        this.name = 'ApiHttpError';
        this.message = message || '';
        this.stack = (new Error()).stack;
    }
}

/**
 * when access token doesn't work
 */
export class AuthError {
    constructor(message) {
        this.name = 'ApiAuthError';
        this.message = message || '';
        this.stack = (new ApiHttpError).stack;
    }
}

/**
 * when server does not understand data given
 */
export class UnprocessableError {
    constructor(message) {
        this.name = 'UnprocessableError';
        this.message = message || '';
        this.stack = (new ApiHttpError).stack;
    }
}
