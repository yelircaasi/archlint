{
    description = "";
    inputs = {
        nixpkgs = {
            url = "github:nixos/nixpkgs/722b93002a9163040b4789730cb1710573ca56ec";
        };

        flake-utils = {
            url = "github:numtide/flake-utils/11707dc2f618dd54ca8739b309ec4fc024de578b";
        };

        pyproject-nix = {
            url = "github:pyproject-nix/pyproject.nix/e09c10c24ebb955125fda449939bfba664c467fd";
            inputs.nixpkgs.follows = "nixpkgs";
        };

        uv2nix = {
            url = "github:pyproject-nix/uv2nix/582024dc64663e9f88d467c2f7f7b20d278349de";
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };

        pyproject-build-systems = {
            url = "github:pyproject-nix/build-system-pkgs/7dba6dbc73120e15b558754c26024f6c93015dd7";
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.uv2nix.follows = "uv2nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };
    };
    outputs = {
        self,
        nixpkgs,
        flake-utils,
        pyproject-nix,
        uv2nix,
        pyproject-build-systems,
    }:
        flake-utils.lib.eachDefaultSystem (system: let
            pkgs = import nixpkgs {
                inherit system;
                config.permittedInsecurePackages = [];
                overlays = [];
            };
            uvEnv = import ./nix/uv.nix {
                inherit
                    pkgs
                    pyproject-nix
                    uv2nix
                    pyproject-build-systems
                    ;
            };
        in {
            packages = {
                default = uvEnv.package;
                archlint = uvEnv.package;
            };
            apps = {};
            devShells = {
                default = uvEnv.pureEnv;
                pure = uvEnv.pureEnv;
                impure = uvEnv.impureEnv;
                fhs = uvEnv.fhsEnv;
            };
            legacyPackages = pkgs;
        });
}
