import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';


import { ICommandPalette } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ITranslator } from '@jupyterlab/translation';
import { CommandToolbarButton, codeCheckIcon } from '@jupyterlab/ui-components';
import { Panel } from '@lumino/widgets';
import { BugBotWidget } from './results';
// import * as React from 'react';
// import { DocumentManager } from '@jupyterlab/docmanager';
// import { ILauncher } from '@jupyterlab/launcher';

function activate(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  notebookTracker: INotebookTracker,
  translator: ITranslator,
  restorer: ILayoutRestorer | null,
) {
  console.log(
    'JupyterLab extension @jupyterlab-examples/server-extension is activated!'
  );
  

  const { commands } = app;
  const command: string = 'apod:insert1';

  commands.addCommand(command, {
    label: 'Buggy/Vulnerable Identification',
    icon: codeCheckIcon,
    execute: async () => {
      addSideBar(app)
    }
  });

  // Add the command to the command palette.
  palette.addItem({ command, category: 'AI' });

  // --------Toolbar-------
  // Add the command to the toolbar of the notebook
  notebookTracker.widgetAdded.connect((sender, notebookPanel) => {
    const toolbar = notebookPanel.toolbar;

    // Add a command if it isn't already added
    if (!commands.hasCommand('apod:insert-picture')) {
      commands.addCommand('apod:insert-picture', {
        label: 'Bug-Bot',
        icon: codeCheckIcon, // Set an icon if you want
        execute: async () => {
          // Add functionality for the command, like inserting an image or executing something.
        },
        caption: 'Notebook Optimisation' // Tooltip
      });
    }

    // Add the button to the toolbar
    toolbar.addItem(
      'apodButton',
      new CommandToolbarButton({
        commands: app.commands,
        id: 'apod:insert-picture' // The command ID we just added
      })
    );
  });
}

function addSideBar(app: any) {
  `Adding sidebar panel to show results in Jupyter environment`
  const panelId = 'Results-tab';
  const existingPanel = Array.from(app.shell.widgets('left')).find((widget: any) => widget.id === panelId);
  if (existingPanel) {
    return;
  }
  const panel = new Panel();
  panel.id = panelId;
  panel.title.icon = codeCheckIcon;
  panel.addWidget(new BugBotWidget());
  app.shell.add(panel, 'left', { rank: 2000 })
  app.shell.activateById('Results-tab')
}



/**
 * Initialization data for the jupyterbugbot extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterbugbot:plugin',
  description: 'A JupyterLab extension that uses AI agents to detect buggy and vulnerable code.',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker],
  optional: [ILayoutRestorer],
  activate: activate
}



export default plugin;
