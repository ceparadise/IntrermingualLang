package org.apache.maven.bootstrap.compile;

/*
 * Copyright 2001-2005 The Apache Software Foundation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

/**
 * @author jdcasey
 */
public class CompilerConfiguration
{

    private String outputLocation;

    private List classpathEntries = new LinkedList();

    private List sourceLocations = new LinkedList();

    private Set includes = new HashSet();
    private Set excludes = new HashSet();

    private Map compilerOptions = new TreeMap();

    private boolean debug = false;

    private Set sourceFiles = new HashSet();

    private boolean noWarn;

    public void setSourceFiles(Set sourceFiles)
    {
        this.sourceFiles = sourceFiles;
    }
    
    public Set getSourceFiles()
    {
        return sourceFiles;
    }
    
    public void setOutputLocation(String outputLocation)
    {
        this.outputLocation = outputLocation;
    }
    
    public String getOutputLocation()
    {
        return outputLocation;
    }
    
    public void addClasspathEntry(String classpathEntry)
    {
        this.classpathEntries.add(classpathEntry);
    }
    
    public void setClasspathEntries(List classpathEntries) {
        this.classpathEntries = new LinkedList(classpathEntries);
    }
    
    public List getClasspathEntries() {
        return Collections.unmodifiableList(classpathEntries);
    }
    
    public void addSourceLocation(String sourceLocation) {
        this.sourceLocations.add(sourceLocation);
    }
    
    public void setSourceLocations(List sourceLocations) {
        this.sourceLocations = new LinkedList(sourceLocations);
    }
    
    public List getSourceLocations() {
        return Collections.unmodifiableList(sourceLocations);
    }
    
    public void addInclude(String include) {
        this.includes.add(include);
    }
    
    public void setIncludes(Set includes) {
        this.includes = new HashSet(includes);
    }
    
    public Set getIncludes() {
        return Collections.unmodifiableSet(includes);
    }
    
    public void addExclude(String exclude) {
        this.excludes.add(exclude);
    }
    
    public void setExcludes(Set excludes) {
        this.excludes = new HashSet(excludes);
    }
    
    public Set getExcludes() {
        return Collections.unmodifiableSet(excludes);
    }
    
    public void addCompilerOption(String optionName, String optionValue) {
        this.compilerOptions.put(optionName, optionValue);
    }
    
    public void setCompilerOptions(Map compilerOptions) {
        this.compilerOptions = new TreeMap(compilerOptions);
    }
    
    public Map getCompilerOptions() {
        return Collections.unmodifiableMap(compilerOptions);
    }
    
    /**
     * @param debug The debug to set.
     */
    public void setDebug( boolean debug )
    {
        this.debug = debug;
    }

    /**
     * Compile with debug info
     * 
     * @return Returns the debug.
     */
    public boolean isDebug()
    {
        return debug;
    }

    public void setNoWarn( boolean noWarn )
    {
        this.noWarn = noWarn;
    }

    public boolean isNoWarn()
    {
        return noWarn;
    }
    
}
