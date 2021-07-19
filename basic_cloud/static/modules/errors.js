/**
 * when the login fails
 * (either incorrect username or password)
 */
export class InvalidLoginError {
    constructor(message) {
        this.name = 'InvalidLoginError';
        this.message = message || '';
        this.stack = (new Error()).stack;
    }
}
