# cheshirecat-plugin
Cheshire Cat plugin for regolo.ai


## Overview

This plugin enables integration with regolo.ai from cheshire cat.
It allows users to select models for chat and embedding.

## Installation

1. Ensure that the cheshire cat is properly installed and set up. (https://cheshire-cat-ai.github.io/docs/quickstart/installation-configuration/)

2. Search for "regolo" in cheshire cat's plugin section, then press on the "install" button.

## Configuration

#### 1. Insert API Key to authenticate the plugin:
    Navigate to the "Plugins" section in cheshire cat, then:

    - Click on the Options icon.

    - Enter your API key in the designated field.

    - Save your settings. (It is mandatory to click on the "save" button after you entered your api key)

#### 2. Configure an llm

    Navigate to the "Settings" section in cheshire cat, then:

    - Go to the "Large Language Model".

    - Select "Regolo LLM" from the menu.

    - Choose the desired llm model from the ones listed.

#### 3. Configure an embedder

    Navigate to the "Settings" section in cheshire cat, then:

    - Open the "Embedder" section.

    - Select "Regolo embedder models" from the menu.

    - Choose the desired embedder model from the ones listed.

> [!TIP]
> if you cannot see some models listed on https://regolo.ai,
> check if your API key was generated with the models you need.
> 
> If it isn't, you can generate another one by logging in to your regolo dashboard.

# Usage

After configuring the settings, the plugin will be ready for use.
You can now leverage AI models and embeddings for your tasks on cheshire cat.

# Troubleshooting

- If the API key is incorrect, re-enter it in the Options section.

- If you get errors after updating the plugin, it is recommended to reinstall the plugin, and, if the issues
persist, to re-start your docker container (Remember to back up your data).