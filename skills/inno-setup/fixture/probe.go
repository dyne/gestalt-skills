// A dependency-free payload for exercising both Windows subsystems.
package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
)

func main() {
	if len(os.Args) == 2 {
		switch os.Args[1] {
		case "--version":
			fmt.Println("fixture diagnostic")
			return
		case "--echo":
			if _, err := io.Copy(os.Stdout, os.Stdin); err != nil {
				os.Exit(1)
			}
			return
		}
	}
	exe, err := os.Executable()
	if err != nil || os.WriteFile(filepath.Join(filepath.Dir(exe), "launch.txt"), []byte(filepath.Base(exe)), 0600) != nil {
		os.Exit(1)
	}
}
