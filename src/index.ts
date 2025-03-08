import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';


import { ICommandPalette } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
// import { ITranslator } from '@jupyterlab/translation';
// import { CommandToolbarButton, codeCheckIcon } from '@jupyterlab/ui-components';
// import { DocumentManager } from '@jupyterlab/docmanager';
// import { ILauncher } from '@jupyterlab/launcher';

import { requestAPI } from './handler';

// function activate(
//   app: JupyterFrontEnd,
//   palette: ICommandPalette,
//   notebookTracker: INotebookTracker,
//   translator: ITranslator,
//   restorer: ILayoutRestorer | null
// ) {
//   const { commands } = app;
//   const command: string = 'apod:insert1';

//   commands.addCommand(command, {
//     label: 'Buggy/Vulnerable Identification',
//     icon: codeCheckIcon,
//     execute: async () => {
//       requestAPI<any>('get-example')
//         .then(data => {
//           console.log(data);
//         })
//         .catch(reason => {
//           console.error(
//             `The jupyterlab_examples_server server extension appears to be missing.\n${reason}`
//           );
//         });
//     }
//   });

//   // Add the command to the command palette.
//   palette.addItem({ command, category: 'AI' });

//   // --------Toolbar-------
//   // Add the command to the toolbar of the notebook
//   notebookTracker.widgetAdded.connect((sender, notebookPanel) => {
//     const toolbar = notebookPanel.toolbar;

//     // Add a command if it isn't already added
//     if (!commands.hasCommand('apod:insert-picture')) {
//       commands.addCommand('apod:insert-picture', {
//         label: 'Bug-Bot',
//         icon: codeCheckIcon, // Set an icon if you want
//         execute: async () => {
//           requestAPI<any>('get-example')
//             .then(data => {
//               console.log('here');
//               console.log(data);
//             })
//             .catch(reason => {
//               console.error(
//                 `The jupyterlab_examples_server server extension appears to be missing.\n${reason}`
//               );
//             });
//           // Add functionality for the command, like inserting an image or executing something.
//         },
//         caption: 'Notebook Optimisation' // Tooltip
//       });
//     }

//     // Add the button to the toolbar
//     toolbar.addItem(
//       'apodButton',
//       new CommandToolbarButton({
//         commands: app.commands,
//         id: 'apod:insert-picture' // The command ID we just added
//       })
//     );
//   });
// }

// //Asynchronous function that creates a new notebook then calls methods to add AI
// async function addAI(notebookTracker: INotebookTracker, app: JupyterFrontEnd) {
//   requestAPI<any>('get-example')
//     .then(data => {
//       console.log(data);
//     })
//     .catch(reason => {
//       console.error(
//         `The jupyterlab_examples_server server extension appears to be missing.\n${reason}`
//       );
//     });
//   const activeNotebook = notebookTracker.currentWidget;
//   if (!activeNotebook) {
//     console.warn('No active notebook.');
//     return;
//   }
//   let path = activeNotebook?.context.contentsModel?.path; //gets the path of the notebook to add as input for loading
//   if (!path) {
//     path = "";
//   }

//   let name = activeNotebook?.context.contentsModel?.name; //gets the name of the notebook to add as input for loading
//   if (!name) {
//     name = "Untitled";
//   }

//   //Create a new notebook
//   // const services = app.serviceManager;
//   // await services.ready;
//   // const kernelspecs = services.kernelspecs;
//   // // Note: add null handling - should not use ! in production
//   // const kernels = Object.keys(kernelspecs.specs!.kernelspecs!);
//   // const result = await app.commands.execute('docmanager:new-untitled', {
//   //   path: "results/",
//   //   type: 'notebook'
//   // });


//   // await app.commands.execute('docmanager:open', {
//   //   path: result.path,
//   //   factory: 'Notebook',
//   //   kernel: {
//   //     name: kernels[0]
//   //   }
//   // });
//   // await app.serviceManager.contents.rename(result.path,"results/"+path);

//   console.log(path);
//   const dataToSend = { name: path };
//   requestAPI<any>('get-example', {
//     body: JSON.stringify(dataToSend),
//     method: 'POST'
//   })
//     .then(reply => {
//       console.log(reply);
//     })
//     .catch(reason => {
//       console.error(
//         `Error on POST /jupyterlab-examples-server/hello ${dataToSend}.\n${reason}`
//       );
//     });
// }

/**
 * Initialization data for the jupyterbugbot extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterbugbot:plugin',
  description: 'A JupyterLab extension that uses AI agents to detect buggy and vulnerable code.',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker],
  optional: [ILayoutRestorer],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
  ) => {
    console.log(
      'JupyterLab extension @jupyterlab-examples/server-extension is activated!'
    );
  // activate

    // Try avoiding awaiting in the activate function because
    // it will delay the application start up time.
    requestAPI<any>('get-example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The jupyterlab_examples_server server extension appears to be missing.\n${reason}`
        );
      });

    // POST request
    // const dataToSend = { name: 'George' };
    // requestAPI<any>('hello', {
    //   body: JSON.stringify(dataToSend),
    //   method: 'POST'
    // })
    //   .then(reply => {
    //     console.log(reply);
    //   })
    //   .catch(reason => {
    //     console.error(
    //       `Error on POST /jupyterlab-examples-server/hello ${dataToSend}.\n${reason}`
    //     );
    //   });
    }
}



export default plugin;
