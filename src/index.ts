import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';


import { ICommandPalette } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ITranslator } from '@jupyterlab/translation';
import { CommandToolbarButton, codeCheckIcon,bugDotIcon } from '@jupyterlab/ui-components';
import { Panel } from '@lumino/widgets';
import { BugspyterWidget } from './results';

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
    label: 'Bugspyter',
    icon: codeCheckIcon,
    execute: async () => {
      addSideBar(app,notebookTracker)
    }
  });

  // Add the command to the command palette.
  palette.addItem({ command, category: 'AI' });

  // --------Toolbar-------
  // Add the command to the toolbar of the notebook
  notebookTracker.widgetAdded.connect((sender, notebookPanel) => {
    const toolbar = notebookPanel.toolbar;

    // Add a command if it isn't already added
    if (!commands.hasCommand('apod:insert1')) {
      commands.addCommand('apod:insert1', {
        label: 'Bugspyter',
        icon: bugDotIcon, // Set an icon if you want
        execute: async () => {
          // Add functionality for the command, like inserting an image or executing something.
        },
        caption: 'Buggy/Vulnerable Analysis' // Tooltip
      });
    }

    // Add the button to the toolbar
    toolbar.addItem(
      'apodButton1',
      new CommandToolbarButton({
        commands: app.commands,
        id: 'apod:insert1' // The command ID we just added
      })
    );
  });
}

function addSideBar(app: any,notebookTracker:INotebookTracker) {
  `Adding sidebar panel to show results in Jupyter environment`

  const activeNotebook = notebookTracker.currentWidget;
  if (!activeNotebook) {
    console.warn('No active notebook.');
    return;
  }
  let path = activeNotebook?.context.contentsModel?.path; //gets the path of the notebook to add as input for loading
  if (!path) {
    path = "";
  }

  let validPath=path

  const panelId = 'Results-tab';
  const existingPanel = Array.from(app.shell.widgets('left')).find((widget: any) => widget.id === panelId) as Panel | undefined;
  if (existingPanel) {
    existingPanel.dispose();
  }
  const panel = new Panel();
  panel.id = panelId;
  panel.title.icon = codeCheckIcon;
  panel.addWidget(new BugspyterWidget(validPath));
  app.shell.add(panel, 'left', { rank: 2000 })
  app.shell.activateById('Results-tab')
}



/**
 * Initialization data for the bugspyter extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'bugspyter:plugin',
  description: 'A JupyterLab extension that uses AI agents to detect buggy and vulnerable code.',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker],
  optional: [ILayoutRestorer],
  activate: activate
}



export default plugin;
