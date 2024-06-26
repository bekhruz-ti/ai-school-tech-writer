import os
import base64
from openai import OpenAI


def format_data_for_openai(diffs, readme_content, commit_messages):
    prompt = None
    changes = '\n'.join([
        f'File: {file["filename"]}\nDiff: \n{file["patch"]}\n'
        for file in diffs
    ])
    commit_messages = '\n'.join(commit_messages) + '\n\n'
    readme_content = base64.b64decode(readme_content.content).decode('utf-8')

    prompt = f"""Please review the following code changes and commit messages from a GitHub pull request:
        ## Code changes from Pull Request:
            {changes}
        
        ## Commit messages:
            {commit_messages}"
        
        ## Here is the original README file content:
            {readme_content}

        Consider the code changes and commit messages, determine if the README needs to be updated. If so, edit the README, ensuring to maintain its existing style and clarity.
        
        Updated README:
    """

    return prompt


def call_openai(prompt):
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages = [
            {"role": "system", "content": "You are an AI trained to update README files based on commit messages and code changes."},
            {"role": "user", "content": prompt}
        ]
    )

    response = completion.choices[0].message.content

    return response

def update_readme_and_create_pr(repo, updated_readme, readme_sha):
    commit_message = "AI COMMIT: Proposed README update based on the latest code changes."
    
    commit_sha = os.getenv('COMMIT_SHA')
    main_branch = repo.get_branch('main')
    new_branch_name = f'update-readme-{commit_sha[:7]}'
    new_branch = repo.create_git_ref(ref=f'refs/heads/{new_branch_name}', sha=main_branch.commit.sha)
    
    repo.update_file("README.md", commit_message, updated_readme, readme_sha, branch=new_branch_name)
    
    pull_request = repo.create_pull(
        title="AI PR: Update README based on recent change", 
        body="This is an AI PR. Please review the README", head=new_branch_name, base="main")
    
    return pull_request
