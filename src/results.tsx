import { ReactWidget } from '@jupyterlab/ui-components';
import { requestAPI } from './handler';

import React, { useState } from 'react';

export class BugBotWidget extends ReactWidget {
    render(): JSX.Element {
        return (
            <BugBotComponent />
        );
    }
}

function BugBotComponent() {
    const [showForm, setShowForm] = useState(true);
    const [key, setKey] = useState('');
    const [message,setMessage]= useState('');

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        requestAPI<any>('request_api', {
            body: JSON.stringify({ "key": key }),
            method: 'POST'
        })
            .then(reply => {
                setMessage(reply.result)
            })
            .catch(reason => {
                console.error(
                    `Error on POST /jupyterlab-examples-server/jupyterbugbot`
                );
            });
        setShowForm(false);
    }
    return (
        <body id="main">
            <div className="jp-Examplewidget"><h2>Code Bugs and Vulnerability Assessment</h2></div>
            {showForm ? (
            <form onSubmit={handleSubmit}>
                <label>
                    Enter your API Key: <input name="key" type='password' onChange={(e) => setKey(e.target.value)} />
                </label>
            </form>
            ):
            (<div className="jp-Examplewidget"><h4>{message}</h4></div>)
        }
        </body>
    );
}