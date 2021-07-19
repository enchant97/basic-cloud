export var POPUP_MESSAGE_TYPE_CLASS = {
    INFO: "info",
    WARNING: "warning",
    ERROR: "error",
}

/**
 * Store button information.
 * Used in the Popup class
 */
export class ButtonChoice {
    /**
     * Create a button choice
     * @param {string} caption - text to place on the button
     * @param {Function} callback - callback when the button is clicked
     * @param {any[]} callback_args - arguments to pass on click to the callback
     * @param {boolean} is_disabled - whether the button is disabled
     */
    constructor(caption, callback, callback_args, is_disabled = false) {
        this.caption = caption;
        this.callback = callback;
        this.callback_args = callback_args;
        this.is_disabled = is_disabled;
    }
    /**
     * create a button from values stored
     * @param {Function} callback_on_click - a extra callback on click (used to delete popup)
     * @returns the created button
     */
    create_button(callback_on_click) {
        const button = document.createElement("button");
        button.innerText = this.caption;
        button.addEventListener("click", _ => {
            this.callback(...this.callback_args);
            callback_on_click();
        });
        if (this.is_disabled){ button.setAttribute("disabled", true); };
        return button;
    }
}

export default class Popup {
    /**
     * add a popup to the document body
     * @param {Element} popup_content - the popup content
     * @returns the popup element
     */
    static append_base(popup_content) {
        const popup = document.createElement("div");
        const popup_inner = document.createElement("div");

        popup.classList.add("popup");
        popup_inner.classList.add("inner");
        popup_inner.append(popup_content);

        popup.append(popup_inner);
        document.body.append(popup);
        return popup;
    }
    /**
     * appends a popup with a message
     * @param {string} title - the pop-up title
     * @param {string} description - the pop-up description
     * @param {string} type - the type of message
     * @returns the popup element
     */
    static append_message(title, description, type = POPUP_MESSAGE_TYPE_CLASS.INFO) {
        const content_element = document.createElement("div");
        const title_element = document.createElement("h3");
        const desc_element = document.createElement("p");
        const ok_button = document.createElement("button");

        content_element.classList.add("down", type);
        title_element.innerText = title;
        desc_element.innerText = description;
        ok_button.innerText = "OK";

        content_element.append(title_element);
        content_element.append(desc_element);
        content_element.append(ok_button);

        const popup = this.append_base(content_element);

        ok_button.addEventListener("click", _ => { popup.remove(); });

        return popup;
    }
    /**
     * appends a popup with a loading message
     * @param {string} title - the pop-up title
     * @param {string} description - the pop-up description
     * @returns the popup element
     */
    static append_loading(title, description) {
        const content_element = document.createElement("div");
        const title_element = document.createElement("h3");
        const desc_element = document.createElement("p");
        const loader_element = document.createElement("div");

        content_element.classList.add("down");
        title_element.innerText = title;
        desc_element.innerText = description;
        loader_element.classList.add("spin-load");

        content_element.append(title_element);
        content_element.append(desc_element);
        content_element.append(loader_element);
        return this.append_base(content_element);
    }
    /**
     * appends a popup for providing login details
     * @param {string} title - the pop-up title
     * @param {string} description - the pop-up description
     * @param {function} login_handler - callback for when details have been provided
     * @param {function} create_account_handler - callback for when user wants to create an account
     * @returns the popup element
     */
    static append_login(title, caption, login_handler, create_account_handler) {
        const content_element = document.createElement("div");
        const title_element = document.createElement("h3");
        const caption_element = document.createElement("p");
        const username_label = document.createElement("label");
        const username_element = document.createElement("input");
        const password_label = document.createElement("label");
        const password_element = document.createElement("input");
        const rememberme_label = document.createElement("label");
        const rememberme_element = document.createElement("input")
        const ok_button = document.createElement("button");
        const create_account_button = document.createElement("button");

        content_element.classList.add("down", "gaps");
        title_element.innerText = title;
        caption_element.innerText = caption;
        username_label.innerText = "Username";
        username_label.for = "username";
        username_element.type = "text";
        username_element.id = "username";
        username_element.placeholder = "Username...";
        password_label.innerText = "Password"
        password_label.for = "password";
        password_element.type = "password";
        password_element.id = "password"
        password_element.placeholder = "Password...";
        rememberme_label.innerText = "Remember Me"
        rememberme_label.for = "rememberme";
        rememberme_element.id = "rememberme";
        rememberme_element.type = "checkbox";
        ok_button.innerText = "Login";
        create_account_button.innerText = "Create Account";


        content_element.append(title_element);
        content_element.append(caption_element);
        content_element.append(username_label);
        content_element.append(username_element);
        content_element.append(password_label);
        content_element.append(password_element);
        content_element.append(rememberme_label);
        content_element.append(rememberme_element);
        content_element.append(ok_button);
        content_element.append(create_account_button);

        const popup = this.append_base(content_element);

        ok_button.addEventListener("click", _ => {
            login_handler(
                username_element.value,
                password_element.value,
                rememberme_element.checked
            )
            popup.remove();
        });
        create_account_button.addEventListener("click", _ => {
            create_account_handler();
            popup.remove();
        });

        return popup;
    }
    /**
     * appends a popup for providing account creation details
     * @param {string} title - the pop-up title
     * @param {string} description - the pop-up description
     * @param {function} create_account_handler - callback for when details have been provided
     * @param {function} login_handler - callback for when user wants to login
     * @returns the popup element
     */
    static append_create_account(title, caption, create_account_handler, login_handler) {
        const content_element = document.createElement("div");
        const title_element = document.createElement("h3");
        const caption_element = document.createElement("p");
        const username_label = document.createElement("label");
        const username_element = document.createElement("input");
        const password_label = document.createElement("label");
        const password_element = document.createElement("input");
        const password_confirm_label = document.createElement("label");
        const password_confirm_element = document.createElement("input");
        const ok_button = document.createElement("button");
        const login_button = document.createElement("button");

        content_element.classList.add("down", "gaps");
        title_element.innerText = title;
        caption_element.innerText = caption;
        username_label.innerText = "Username"
        username_label.for = "username";
        username_element.type = "text";
        username_element.id = "username";
        username_element.placeholder = "Username...";
        password_label.innerText = "Password";
        password_label.for = "password";
        password_element.type = "password";
        password_element.id = "password"
        password_confirm_label.innerText = "Password Confirm";
        password_confirm_label.for = "password-confirm";
        password_element.placeholder = "Password...";
        password_confirm_element.type = "password";
        password_confirm_element.id = "password-confirm";
        password_confirm_element.placeholder = "Password Confirm...";
        ok_button.innerText = "Create Account";
        login_button.innerText = "Login";

        content_element.append(title_element);
        content_element.append(caption_element);
        content_element.append(username_label);
        content_element.append(username_element);
        content_element.append(password_label);
        content_element.append(password_element);
        content_element.append(password_confirm_label);
        content_element.append(password_confirm_element);
        content_element.append(ok_button);
        content_element.append(login_button);

        const popup = this.append_base(content_element);

        ok_button.addEventListener("click", _ => {
            create_account_handler(
                username_element.value,
                password_element.value,
                password_confirm_element.value
            )
            popup.remove();
        });
        login_button.addEventListener("click", _ => {
            login_handler();
            popup.remove();
        });

        return popup;
    }
    /**
     * append a selection popup that the user can select from many buttons
     * @param {string} title - the pop-up title
     * @param {string} caption - the pop-up caption
     * @param {ButtonChoice[]} button_choices - the buttons to place
     * @param {boolean} cancelable - whether user can close popup
     */
    static append_selection(title, caption, button_choices, cancelable = true) {
        const content_element = document.createElement("div");
        const title_element = document.createElement("h3");
        const caption_element = document.createElement("p");
        const close_bnt = document.createElement("button");

        content_element.classList.add("down", "gaps");
        title_element.innerText = title;
        caption_element.innerText = caption;
        close_bnt.innerText = "Close";

        if (!cancelable) {
            close_bnt.setAttribute("disabled", true);
        }

        const popup = this.append_base(content_element);

        content_element.append(title_element);
        content_element.append(caption_element);
        button_choices.forEach(button_choice => {
            content_element.append(button_choice.create_button(() => { popup.remove(); }));
        });
        content_element.append(close_bnt);
        close_bnt.addEventListener("click", _ => { popup.remove(); });

        return popup;
    }
}
