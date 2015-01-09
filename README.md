Metis
=======================

The source for Metis, a project to create a social media and verified news engine.

Development Environment (Mac):

1) Configure .bash_profile according to Homebrew instructions
http://hackercodex.com/guide/mac-osx-mavericks-10.9-configuration/

2) Install Homebrew:
http://brew.sh

3) Run:
brew install python

4) Enter a directory you wish to place files into for the project.

5) Run:
pip install virtualenv

6) Create some directories to store our projects and virtual environments, respectively:
mkdir -p ~/Projects ~/Virtualenvs

7) We’ll then open the ~/.bashrc file (which may be created if it doesn’t exist yet)…
vim ~/.bashrc

8)… and add the following lines to it:

# pip should only run if there is a virtualenv currently activated
export PIP_REQUIRE_VIRTUALENV=true
# cache pip-installed packages to avoid re-downloading
export PIP_DOWNLOAD_CACHE=$HOME/.pip/cache

9) Let’s re-load our bash environment:
source ~/.bash_profile

10) Now we have virtualenv installed and ready to create new virtual
environments, which we will store in ~/Virtualenvs. New virtual environments can be created via:
cd ~/Virtualenvs
virtualenv foobar

11) Next, we set up our virtualenv. Run the following command:
virtualenv venv --distribute

12) Followed by:
source venv/bin/activate

Every time you come back to work on this project, you’ll need to run the previous command to make sure you’re running the version of Python installed under venv/ rather than your system Python. You can tell it’s using this because your shell prompt will be prefixed with (venv).

13) run:
pip install Django
to get 1.7

14) Run:
pip install markdown2
to install the markdown2 parser for python

15) Install NPM and Bower for JS dependencies:
brew install npm

16) Setup the NODE_PATH in .bashrc by adding:
NODE_PATH="/usr/local/lib/node_modules"

17) Install bower:
sudo npm install -g bower

18) Run:
bower init
in base project directory to load .bowerrc

19) Run:
bower install bootstrap html5-boilerplate --save
to install dependencies
