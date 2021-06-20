"use strict";

var POPUP_MESSAGE_TYPE_CLASS = {
    INFO: "info",
    WARNING: "warning",
    ERROR: "error",
}

class Popup {
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
}
