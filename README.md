# Glue

Glue is a command-line tool to tie together a number of dependencies that are part of a main project. It makes it possible to define repository-based dependencies, to record/track their version at specific moments in the lifetime of the project, and to produce a build number suitable for app distribution (monotonically increasing). Glue's loose coupling approach makes it easy to setup and deploy, even in unusual project configurations.

You'd typically use Glue when creating an app (the project) that makes use of a number of reusable libraries (the dependencies), but it's certainly not limited to apps. The dependencies should be located relatively to the project root, and have their own repository by themselves. Setting up Glue for the project will let you store dependencies versions when you commit the project itself, effectively establishing a "versioning" link: project commit *ABC* references dependency commit *DEF*.

Lastly, Glue can be invoked as part of the build (through an Xcode script phase, or other build system) when publishing a release. This lets you automate dependency recording, as well as feeding Glue's associated build version directly into the built target.

Glue itself is written in Python, but it is meant to work with any project, in any language.

<p align="center"><img src="https://user-images.githubusercontent.com/369828/61873112-65ca2080-aee5-11e9-885b-2fd8e6c62721.jpg" width="75%"></p>

## Motivation

As app developers, we often make use of libraries to build an app. These libraries can be in house or third party, and are typically published as repositories. Being able to build an exact version of an app that previously shipped is important to inspect, reproduce and hopefully fix specific issues. Or just to keep track of releases. Other dependency tracking solutions exist, either from git itself with git submodule, git subtree, or git subrepo, or by using package manager such as Carthage, CocoaPods, or more recently, [Swift Package Manager](https://swift.org/package-manager/). These tools can serve great purpose within their own constraints, but it's not always practical to deploy them in all circumstances. 

For instance, we typically use symlinks to share common dependencies in multiple projects for faster (but more risky) convergence, and that isn't possible to handle with git submodule. Or we use Xcode projects with a lot of customizations (build phases, targets), and we typically don't want it to be modified by external tools like CocoaPods. Finally, Swift Package Manager is very promising, especially for Swift libs, but it may not be suitable to build all kinds of C/C++ dependencies.

We wanted a tool that was loosely coupled, simple to handle, and with enough flexibility to tackle diverse situations and conventions. That's how it started.

## Theory of Operations

Glue is one-level deep, it is *not* a recusrive system. The main project is simply called the *project* and the subprojects it depends upon are called the *dependencies*. Dependencies are defined (by the developer) in the *.gluedeps* file at the project root, and dependencies versions & metadata are recorded (by invoking glue) alongside in the *.gluestates* file. Both files typically are manually committed as part of the project. And yes, they are HJSON ([Human JSON](https://hjson.org), so, comma not needed, and comments welcome!)

Example **.gluedeps** file that defines dependencies of the project:
```
dep1: {
	path: "relative/path/to/dep1" # can be a symlink
	type: git
	branch: master
	url: "http://path/to/dep1"
}
dep2: {
	path: "relative/path/to/dep2"
	type: hg
	branch: default
	url: "http://path/to/dep2"
}
```

Example of generated **.gluestates** file when recording current state of dependencies:
```
dep1: {
	branch: master
	date: 2019-06-25 18:10:48 +0200
	revision: 2fe339ccb4d0d4a1c101ae17b964878d9238aba6
}
dep2: {
	branch: default
	date: 2019-07-18 19:01:27 +0200
	revision: 4f0222f85be44c2b8ea8f05c8b05c7427fd38222
}
```

## Installation

You can build Glue into a single file executable (no deps) by invoking `build.sh`, and then copy it to your `$PATH` to be able to invoke it from anywhere:
```bash
$ cp ./glue /usr/local/bin
```

## Usage

Get command instructions:

```bash
$ glue --help
``` 

You should get this:

```
usage: glue [-h] {list,status,advance,record,update,check,buildversion} ...

Glue: Automating dependent repositories operations.

positional arguments:
  {list,status,advance,record,update,check,buildversion}
                        sub-command help
    list                Lists all project dependencies, as declared in the
                        .gluedeps file.
    status              Print status for each dependency.
    advance             Advances passed dependencies to their current branch
                        head. Switching branches must be done manually through
                        versioning scheme.
    record              Record project dependencies and generate new
                        .gluestates file.
    update              Update project dependencies to given (or current)
                        recorded states.
    check               Check if dependencies are committed, returns error
                        otherwise with list of uncommitted dependencies.
    buildversion        Return the computed build version. The default scheme
                        for the build version is a 2 part string: <A>.<B>,
                        where A is the number of commits leading to the
                        current one, and <B> is decimal value computed from
                        the commit hash. The former is monotonically
                        increasing when new commits inherit from previous
                        ones, and the latter can give a clue to lookup the
                        commit from its hash in the commit log.

optional arguments:
  -h, --help            show this help message and exit
```

You can also get individual command help like this (some have useful options for script invocations):
```
$ glue <command> --help
```

To check dependencies status:
```
$ glue status

Fetching…
CeedBase (at CeedBase/, type=git):
	status: clean
	current branch: master
	revision: f7fbb31e53081a990d2c111b22c8c55bdf4e74bc
CeedCloud (at CeedCloud/, type=git):
	status: clean 
	current branch: master
	revision: 102f7d589754d83603f693846ddf2b14bc96df70
CeedDatabase (at CeedDatabase/, type=git):
	status: clean 
	current branch: master
	revision: 1d8638af14c63eb0a46529de5dbfa44c35f169eb
```

Recording dependencies states before committing the project:
```
$ glue record
```


To generate a build version, you'd do it this way:
```
$ glue buildversion

Build Version: 253.414
```

Note that the provided build number generation scheme will guarantee monotonic increase (first part) only if the deployment branch of the project only appends new commits (no history rewriting). The part before the dot basically counts the commits, the part after the dot provides a partial decimal hash that can help identify the actual commit of the project.

## License

Glue is available under the 3-clause BSD license. See the LICENSE file for more information.
