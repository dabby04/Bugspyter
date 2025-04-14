import { ReactWidget } from '@jupyterlab/ui-components';
import { requestAPI } from './handler';

import React, { useState, useEffect } from 'react';
import Markdown from 'markdown-to-jsx';

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
    const [isLoading, setIsLoading] = useState(false);
    const [key, setKey] = useState('');
    const [message, setMessage] = useState('');
    const [buggy_or_not, setBuggyorNot] = useState('');
    const [bugtype, setBugType] = useState('');
    const [rootCause, setRootCause] = useState('');
    const [analysis, setAnalysis] = useState('');

    type LLMOptions = {
        [dict_key: string]: string[]
    };
    //adding elements of form for Model picker
    const [step, setStep] = useState(1); // Tracks the current step
    const [selectedLLM, setSelectedLLM] = useState(""); // Selected LLM
    const [selectedModel, setSelectedModel] = useState(""); // Selected model

    const llmOptions: LLMOptions = {
        Anthropic: [
            "claude-3-7-sonnet-latest",
            "claude-3-5-haiku-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-latest",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        Cohere: [],
        Groq: [
            "gemma2-9b-it",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-guard-3-8b",
            "llama3-70b-8192",
            "llama3-8b-8192",
        ],
        Nvidia: ["deepseek-ai/deepseek-r1"],
        Gemini: [
            "gemini-2.0-flash",
            "gemini-1.5-flash-002",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro-002",
            "gemini-1.5-pro-001"
        ],
    };

    useEffect(() => {
        if (step === 2 && selectedLLM && llmOptions[selectedLLM].length === 0) {
            setStep(3);
        }
    }, [step, selectedLLM]);

    const path = props.notebook_path;

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        setIsLoading(true);
        try {
            await requestAPI<any>('request_api', {
                body: JSON.stringify({"selectedLLM":selectedLLM,"selectedModel":selectedModel, "key": key }),
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
            await requestAPI<any>('load_notebook', {
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
            await requestAPI<any>('analysis')
                .then(reply => {
                    setAnalysis(reply.result);
                })
                .catch(reason => {
                    console.error(
                        `The jupyterlab_examples_server server extension appears to be missing.\n${reason}`
                    );
                });
        }
        catch (error) {
            // Handle errors
            console.error('Error submitting form:', error);
        } finally {
            setIsLoading(false); // Reset loading state to false
            setShowForm(false);
        }

    }
    return (
        <body id="main">
            <div className="jp-Examplewidget"><h2>Code Bugs and Vulnerability Assessment</h2>
                {showForm ? (
                    <form onSubmit={handleSubmit}>
                        {/* Step 1: Select LLM */}
                        {step === 1 && (
                            <div>
                                <label>
                                    Choose an LLM:
                                    <select
                                        value={selectedLLM}
                                        onChange={(e) => {
                                            setSelectedLLM(e.target.value);
                                            setSelectedModel(""); // Reset model when LLM changes
                                            setStep(2); // Move to next step
                                        }}
                                    >
                                        <option value="">--Select an LLM--</option>
                                        {Object.keys(llmOptions).map((llm) => (
                                            <option key={llm} value={llm}>
                                                {llm}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                            </div>
                        )}

                        {/* Step 2: Select Model (if applicable) */}
                        {step === 2 && selectedLLM && llmOptions[selectedLLM].length > 0 && (
                            <div>
                                <label>
                                    Choose a model:
                                    <select
                                        value={selectedModel}
                                        onChange={(e) => {
                                            setSelectedModel(e.target.value);
                                            setStep(3); // Move to next step
                                        }}
                                    >
                                        <option value="">--Select a model--</option>
                                        {llmOptions[selectedLLM].map((model) => (
                                            <option key={model} value={model}>
                                                {model}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                            </div>
                        )}

                        {/* Step 3: Enter API Key */}
                        {step === 3 && (
                            <div>
                                <label>
                                    Enter your API Key:
                                    <input
                                        name="key"
                                        type="password"
                                        onChange={(e) => setKey(e.target.value)}
                                        disabled={isLoading}
                                    />
                                </label>
                                {isLoading && <p>Loading results...</p>}
                                <button type="submit" disabled={isLoading || !key}>
                                    Submit
                                </button>
                            </div>
                        )}
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
                        <Markdown>{analysis}</Markdown>
                    </div>
                    )
                }
            </div>
        </body>
    );
}