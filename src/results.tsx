import { ReactWidget } from '@jupyterlab/ui-components';
import { requestAPI } from './handler';

import React, { useState } from 'react';

export class BugBotWidget extends ReactWidget {
    private notebook_path: string;

    constructor(notebook_path: string) {
        super();
        this.notebook_path = notebook_path;
    }

    render(): JSX.Element {
        return (
            <BugBotComponent notebook_path={this.notebook_path} />
        );
    }
}

interface BugBotComponentProps {
    notebook_path: string;
}

function BugBotComponent(props: BugBotComponentProps) {
    const [showForm, setShowForm] = useState(true);
    const [key, setKey] = useState('');
    const [message, setMessage] = useState('');
    const [buggy_or_not, setBuggyorNot] = useState('');
    const [bugtype, setBugType] = useState('');
    const [rootCause, setRootCause] = useState('');
    const [analysis,setAnalysis]= useState('');
    const path = props.notebook_path;

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
        requestAPI<any>('load_notebook', {
            body: JSON.stringify({ "notebook_path": path }),
            method: 'POST'
        })
            .then(reply => {
                setBuggyorNot(reply.buggy_or_not),
                setBugType(reply.major_bug),
                setRootCause(reply.root_cause)
            })
            .catch(reason => {
                console.error(
                    `Error on POST /jupyterlab-examples-server/jupyterbugbot`
                );
            });
            requestAPI<any>('analysis')
            .then(reply => {
              setAnalysis(reply.result);
            })
            .catch(reason => {
              console.error(
                `The jupyterlab_examples_server server extension appears to be missing.\n${reason}`
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
            ) :
                (<div className="jp-Examplewidget"><h4>{message}</h4>
                    <div><h3>Is the Notebook buggy?</h3></div>
                    <body>{buggy_or_not}</body>
                    <div><h3>What major bug type is in the notebook?</h3></div>
                    <body>{bugtype}</body>
                    <div><h3>What is the root cause of bugs in the notebook?</h3></div>
                    <body>{rootCause}</body>
                    <div><h3>Bug Analysis</h3></div>
                    <body>{analysis}</body>
                </div>
                )
            }
        </body>
    );
}