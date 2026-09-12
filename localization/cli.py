"""Export, validate and build a disc-derived manual localization workspace."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import patch as english_patch
from . import __version__
from .common import load_language, validate
from .po import read_po, write_po
from .adapter import Project, TITLE
ROOT = Path(__file__).resolve().parent.parent

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=TITLE + ' localization toolkit')
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('export', 'validate', 'build'):
        p = sub.add_parser(command)
        p.add_argument('--bin', type=Path, required=True, help='supported original Japanese BIN')
        p.add_argument('--locale', default='ru')
        p.add_argument('--font', type=Path, help='TTF/OTF font containing the target alphabet')
        if command == 'export':
            p.add_argument('--output', type=Path, required=True)
        else:
            p.add_argument('--workspace', type=Path, required=True)
            p.add_argument('--allow-incomplete', action='store_true', help='retain canonical English for untranslated entries')
        if command == 'build':
            p.add_argument('--output-dir', type=Path, required=True)
        if command != 'validate':
            p.add_argument('--force', action='store_true')
        if command == 'export':
            p.add_argument('--language', type=Path, help='custom language definition; otherwise use bundled locale')
    args = parser.parse_args()
    try:
        if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,63}', args.locale):
            raise ValueError('invalid locale code')
        workspace = (args.output if args.command == 'export' else args.workspace).resolve()
        language_path = args.language or ROOT / 'localization/languages' / f'{args.locale}.json' if args.command == 'export' else workspace / 'language.json'
        language = load_language(language_path, args.locale)
        outputs = [workspace / n for n in ('dialogue.po', 'language.json', 'source_inventory.json')] if args.command == 'export' else []
        if args.command == 'build':
            out = args.output_dir.resolve()
            stem = language['output_stem']
            outputs = [out / (stem + '.bin'), out / (stem + '.cue')]
            if args.bin.resolve() in outputs:
                raise ValueError('output would overwrite the source disc')
        if any((p.exists() for p in outputs)) and (not args.force):
            raise ValueError('output exists; choose a new directory or use --force')
        manifest = english_patch.load_manifest()
        english_patch.verify_file('source BIN', args.bin, manifest['source']['bin'])
        parts = english_patch.verify_patch_parts(manifest['patches']['bin'])
        parent = args.output_dir.resolve() if args.command == 'build' else workspace.parent
        parent.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(parent).free < int(manifest['target']['bin']['size']) + 128 * 1024 * 1024:
            raise ValueError('insufficient temporary disc space')
        with tempfile.TemporaryDirectory(prefix='.localize-', dir=parent) as temp:
            base = Path(temp) / 'base.bin'
            english_patch.apply_xor_delta(args.bin, base, manifest['patches']['bin'], parts, manifest['target']['bin'])
            english_patch.verify_file('English base BIN', base, manifest['target']['bin'])
            project = Project(args.bin, base, manifest)
            entries = project.entries()
            if args.command == 'export':
                workspace.mkdir(parents=True, exist_ok=True)
                write_po(outputs[0], [e.po() for e in entries], args.locale)
                write_json(outputs[1], language)
                write_json(outputs[2], dict(schema=1, game=TITLE, toolkit_version=__version__, locale=args.locale, source=manifest['source']['bin'], english_base=manifest['target']['bin'], entry_count=len(entries), scope=project.scope))
                print(f'Exported {len(entries)} entries to {outputs[0]}')
                return 0
            translations = validate(entries, read_po(workspace / 'dialogue.po'), args.allow_incomplete)
            report = project.compile(translations, language, args.font, Path(temp))
            report.update(schema=1, toolkit_version=__version__, game=TITLE, locale=args.locale, catalog=dict(total=len(entries), translated=len(translations), english_fallback=len(entries) - len(translations)))
            if args.command == 'validate':
                print(json.dumps(report, ensure_ascii=False, indent=2))
                return 0
            project.install(base)
            digest, size = english_patch.sha256_file(base)
            cue = Path(temp) / 'output.cue'
            cue.write_bytes(f'FILE "{outputs[0].name}" BINARY\r\n  TRACK 01 MODE2/2352\r\n    INDEX 01 00:00:00\r\n'.encode('ascii'))
            report['output'] = dict(bin=outputs[0].name, size=size, sha256=digest, cue=outputs[1].name)
            build = workspace / 'build'
            build.mkdir(parents=True, exist_ok=True)
            for proof in Path(temp).glob('*.png'):
                shutil.copyfile(proof, build / proof.name)
            write_json(build / 'build_report.json', report)
            os.replace(base, outputs[0])
            os.replace(cue, outputs[1])
            print(f'Built {outputs[0]}\nSHA-256: {digest}\nEnglish fallback: {len(entries) - len(translations)} entries')
        return 0
    except (ValueError, RuntimeError, OSError, KeyError, TypeError, AssertionError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
if __name__ == '__main__':
    raise SystemExit(main())
