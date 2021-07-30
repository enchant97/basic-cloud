# Api

## Web Api
This part of the api documentation is built into the application, just run the server and go to `http://yourdomain/docs`.

## Websocket Api

### Message Formats
All messages to and from server use JSON by default (more methods may be added later). Message structure will be shown below (including excepted data-types).

Depending on message type the payload will differ. The message payload may also be empty, *depending on the message type*.

> Receive and send message types may have the same int, however there meaning may differ.

> api url = `/api/ws?bearer_token=<token>`

#### Receive

```json
{
    message_type: int,
    when: datetime,
    payload: {}
}
```

#### Send

```json
{
    message_type: int,
    when: datetime,
    payload: {}
}
```

#### Format Examples

This is an example of a change directory message:

```json
{
    message_type: 1,
    when: datetime,
    payload: {
        directory: "shared/testing"
    }
}
```

> If the user is not allowed to navigate into that directory a 401 error will be issued.

A directory update sent from the server will look similar to this:

```json
{
    message_type: 1,
    when: datetime,
    payload: {
        path: "shared/testing",
        change_type: 1
    }
}
```
