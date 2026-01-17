import { ReactWidget } from '@jupyterlab/ui-components';
import { requestAPI } from './handler';

import React, { useState, useEffect } from 'react';
import Markdown from 'markdown-to-jsx';

export class BugspyterWidget extends ReactWidget {
    private notebook_path: string;

    constructor(notebook_path: string) {
        super();
        this.notebook_path = notebook_path;
    }

    render(): JSX.Element {
        return (
            <BugspyterComponent notebook_path={this.notebook_path} />
        );
    }
}

interface BugspyterComponentProps {
    notebook_path: string;
}

function BugspyterComponent(props: BugspyterComponentProps) {
    const [showForm, setShowForm] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [key, setKey] = useState('');
    const [message, setMessage] = useState('');
    const [buggy_or_not, setBuggyorNot] = useState('');
    const [bugtype, setBugType] = useState('');
    const [rootCause, setRootCause] = useState('');
    const [analysis, setAnalysis] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [status, setStatus] = useState('');
    const [decision_status,setDecisionStatus] = useState('');

    type LLMOptions = {
        [dict_key: string]: string[]
    };
    //adding elements of form for Model picker
    const [step, setStep] = useState(1); // Tracks the current step
    const [selectedLLM, setSelectedLLM] = useState(""); // Selected LLM
    const [selectedModel, setSelectedModel] = useState(""); // Selected model
    const [needsApiKey, setNeedsApiKey] = useState(false);
    const yieldToUI = () => Promise.resolve();

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
        Qwen: ["Qwen/Qwen2.5-Coder-32B-Instruct"],
        Gemini: [
            "gemini-3-pro-preview",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-flash-002",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro-002",
            "gemini-1.5-pro-001"
        ],
    };

    useEffect(() =>{
        if(!selectedLLM||!selectedModel){
            return;
        }
        initialiseAPIKey();
    }, [selectedLLM,selectedModel])

    useEffect(() => {
        // if (step === 2 && selectedLLM && llmOptions[selectedLLM].length === 0) {
        //     setStep(3);
        // }
        if(step!==2||!selectedLLM){
            return;
        }
        if(needsApiKey){
            setStep(3);
        }
    }, [step, selectedLLM]);

    async function ensureLLMInitialized(key?: string){
        const body:any = {
                selectedLLM,
                selectedModel
            };

            if (key){
                body.key = key;
            }

            // 1) Initialize LLM with API key
            return await requestAPI<any>('request_api', {
                body: JSON.stringify(body),
                method: 'POST'
            });
    }

    async function initialiseAPIKey(){
        setIsLoading(true);
        setErrorMessage('');

        try{
            const initReply = await ensureLLMInitialized();

            if(initReply.result == 'LLM initialised'){
                setNeedsApiKey(false);
                setMessage(initReply.result);
                await yieldToUI();
                await process();
                
            }
            else if (initReply.result == "Could not initialise LLM"){
                setNeedsApiKey(true);
            }
            else{
                setErrorMessage(initReply.result);
            }
        } catch(err){
            setErrorMessage("Failed to contact server")
        }
        finally{
            setIsLoading(false);
        }
    }

    const path = props.notebook_path;

    async function process(){
        try{
            // 2) Load notebook only after successful init
            const nbReply = await requestAPI<any>('load_notebook', {
                body: JSON.stringify({ notebook_path: path }),
                method: 'POST'
            });
            setStatus(nbReply.status);
            const decision = nbReply.decision;
            if(decision == 'runtime'){
                setDecisionStatus("Running runtime execution tool...")
                await yieldToUI();
            }
            else if(decision =='analysis'){
                setDecisionStatus("Analysing notebook")
                await yieldToUI();
            }

            // 3) Run analysis
            const analysisReply = await requestAPI<any>('router_workflow',{
                body: JSON.stringify({
                    notebook_path: path,
                    decision: decision
                }),
                method: 'POST'
            });
            setBuggyorNot(analysisReply.buggy_or_not);
            setBugType(analysisReply.major_bug);
            setRootCause(analysisReply.root_cause);
            setAnalysis(analysisReply.analysis);

            // Only now switch to results view
            setShowForm(false);
        }
        catch (error: any) {
            console.error('Error submitting form:', error);
            setErrorMessage(String(error?.message ?? error));
            return;
        }
    }

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setErrorMessage('');
        setIsLoading(true);

        try {
            const initReply = await ensureLLMInitialized(key);
            // Guard: stop if LLM not initialized
            if (initReply.result !== 'LLM initialised') {
                setErrorMessage(initReply.result || 'API key not initialised');
                return; // Keep form visible; do not proceed
            }
            setMessage(initReply.result);
            setNeedsApiKey(false);
            setKey("");
            await process();

        } catch (error: any) {
            console.error('Error submitting form:', error);
            setErrorMessage(String(error?.message ?? error));
            return;
        } finally {
            setIsLoading(false);
        }
    }
    return (
        <body id="main">
            <div className="jp-Examplewidget"><h2>Code Bugs and Vulnerability Assessment</h2>
                {showForm ? (
                    <>
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
                        {step === 3 && needsApiKey && (
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
                                {isLoading && <p>{status}</p>}
                                {isLoading && <p>{decision_status}</p>}
                                <button type="submit" disabled={isLoading || !key}>
                                    Submit
                                </button>
                            </div>
                        )}
                        {errorMessage && (
                            <div className="jp-Error">
                                <h4>Error</h4>
                                <body>{String(errorMessage)}</body>
                            </div>
                        )}
                    </form>
                    {isLoading && (
      <div className="jp-Status">
        <h4>{message}</h4>
        <p>{status}</p>
        <p>{decision_status}</p>
      </div>
    )}
    </>
                ) :
                    (<div className="jp-Examplewidget">
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