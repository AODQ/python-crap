#!/usr/bin/rdmd
import std.stdio, std.regex, std.conv, std.process;
static import file = std.file;

StaticRegex!char[string] ctr_list;
static this ( ) {
 ctr_list = [
   "lambda": ctRegex!(`\%`),
   "not":    ctRegex!(`\!(?!=)`),
   "or":     ctRegex!(`\|\|`),
   "and":    ctRegex!(`\&\&`),
 ];
}

void main ( string[] args ) {
  string contents = file.read(args[1]).to!string;
  // -- keywords --
  foreach ( c; ctr_list.byKeyValue() )
    contents = contents.replaceAll(c.value, c.key);

  file.write("toutput.py", contents);
  auto pid = spawnProcess(["python", "toutput.py"]);
  scope(exit) wait(pid);
}
