{
    pkgs,
    pyproject-nix,
    uv2nix,
    pyproject-build-systems,
}: let
    custom = import ./custom-packages.nix {inherit pkgs;};

    pythonPackage = pkgs.python312;

    pythonPackages = pkgs.python312Packages;

    sharedEnv = {};

    dependencies = {
        flex =
            (with custom; [
                mdformat-with-plugins
                mkdocs-with-plugins
            ])
            ++ (with pkgs; [
                uv
                just
                lefthook
                commitizen
                ruff
                toml-sort
                yamlfmt
                yamllint
                pythonPackages.vulture
                pythonPackages.radon
                pythonPackages.radon
                pydeps
                bandit
                cyclonedx-python
                mypy
                ty
            ]);
        nonPython =
            (with custom; [
                justfmt
            ])
            ++ (with pkgs; [
                cargo-flamegraph
                flamegraph
                graphviz
                alejandra
                mdsf # alternative: markdown-code-runner
                treefmt
                shfmt
                jujutsu
                jjui
                graphviz
                perf-tools
                ripgrep
                fd
                bat
                sad
            ]);
    };

    systemPackages = pkgs: (with pkgs; [
        poetry
        stdenv.cc.cc.lib
        zlib
        libuuid
        file
        libz
        gcc
        which
        openssh
    ]);

    inherit (pkgs) lib;

    python = pythonPackage;

    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ../.;};

    overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
    };

    pyprojectOverrides = _final: _prev: {};

    pythonSet = (
        pkgs.callPackage pyproject-nix.build.packages {inherit python;}
    )
        .overrideScope
    (
        lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
            pyprojectOverrides
        ]
    );

    editableOverlay = workspace.mkEditablePyprojectOverlay {
        root = "$REPO_ROOT";
        members = ["archlint"];
    };

    editablePythonSet = pythonSet.overrideScope editableOverlay;

    virtualenvPure = editablePythonSet.mkVirtualEnv
    "archlint-dev-env"
    {archlint = ["test" "dev"];};

    defaultPackage = pythonSet.mkVirtualEnv
    "archlint-pkg-env"
    workspace.deps.default;
in {
    package = defaultPackage;

    pureEnv = pkgs.mkShell {
        packages = [virtualenvPure] ++ dependencies.nonPython ++ dependencies.flex;

        env =
            sharedEnv
            // {
                UV_NO_SYNC = "1";
                UV_PYTHON = "${virtualenvPure}/bin/python";
                UV_PYTHON_DOWNLOADS = "never";

                NIX_PYTHON = "${virtualenvPure}/bin/python";
            };

        shellHook = ''
            source .envrc

            # Undo dependency propagation by nixpkgs.
            unset PYTHONPATH

            # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
            export REPO_ROOT=$(git rev-parse --show-toplevel)
        '';
    };

    impureEnv = pkgs.mkShell {
        packages = [python] ++ dependencies.nonPython;

        env =
            sharedEnv
            // {
                UV_PYTHON_DOWNLOADS = "1";
                UV_PYTHON = python.interpreter;
            }
            // lib.optionalAttrs pkgs.stdenv.isLinux {
                LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
            };

        shellHook = ''
            unset PYTHONPATH
            source .envrc
        '';
    };

    fhsEnv =
        (pkgs.buildFHSUserEnv rec {
            name = "archlint-dev-env-fhs";
            targetPkgs = systemPackages;
            profile = ''
                source .envrc
                export LD_LIBRARY_PATH="/lib:$LD_LIBRARY_PATH:${pkgs.lib.makeLibraryPath [pkgs.libuuid]}"
                uv venv
                uv install
                source .venv/bin/activate
            '';
        }).env;
}
